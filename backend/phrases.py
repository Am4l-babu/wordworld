"""Noun-phrase readers: quantities, relations, colors and counted groups."""
from __future__ import annotations

import re
from fractions import Fraction

from .lexicon import (
    COLORS, COLOR_PARTS, COLOR_RE, COUNT_WORDS, ENTITY_RE, GROUP_MODIFIER_RE,
    NEGATION_RE, NUMBER_RE, NUMERAL, POST_COLOR_RE, POST_QUANTITY_RE,
    POST_QUANTITY_WORDS, RELATION_PATTERNS, TOTAL_OF_PREFIX_RE, UNKNOWN_QUANTITY_RE,
    WORD_TO_TYPE,
)


def number_value(raw: str) -> int | None:
    if re.fullmatch(r"[+-]?\d+(?:\.\d+)?", raw):
        return int(raw) if '.' not in raw and int(raw) >= 0 else None
    value, total = 0, 0
    for word in raw.lower().replace('-', ' ').split():
        if word == 'and':
            continue
        if word == 'hundred':
            value = (value or 1) * 100
        elif word == 'thousand':
            total += (value or 1) * 1000
            value = 0
        else:
            value += COUNT_WORDS[word]
    return total + value


def quantity(prefix: str, entity: str) -> tuple[int | None, re.Match | None]:
    # A numeral must belong to this noun phrase; it cannot cross another noun.
    matches = list(NUMBER_RE.finditer(prefix))
    meaningful = [m for m in matches if not m.group('article')]
    match = (meaningful or matches)[-1] if matches else None
    defaults = {"village": 4, "villages": 4, "town": 4, "towns": 4, "forest": 6, "forests": 6, "woods": 6, "woodland": 6, "woodlands": 6, "garden": 5, "gardens": 5}
    if (UNKNOWN_QUANTITY_RE.search(prefix)
            or re.search(r'\bexactly\b', prefix, re.I) and any(m.group('approx') for m in matches)
            or len(meaningful) > 1):
        return None, match
    if match and len(prefix[match.end():].split()) <= 4:
        if match.group('half'):
            return 6, match
        if match.group('group'):
            multiplier = number_value((match.group('multiplier') or 'one').lower())
            unit = 12 if match.group('group').lower().startswith('dozen') else 2
            return multiplier * unit if multiplier is not None else None, match
        if match.group('number'):
            return number_value(match.group('number').lower()), match
        if match.group('approx'):
            return COUNT_WORDS[match.group('approx').lower()], match
        return defaults.get(entity.lower(), 1), match
    return defaults.get(entity.lower(), 1), None


def relation_in(text: str):
    candidates = [(m.start(), -len(m.group()), name, m)
                  for name, pattern in RELATION_PATTERNS
                  if (m := re.search(pattern, text, re.I))]
    if not candidates:
        return None, None
    _, _, name, match = min(candidates, key=lambda item: item[:2])
    return name, match


def leading_relation(text: str):
    relation, match = relation_in(text)
    if match and re.fullmatch(r"\s*(?:please\s*)?(?:to\s+(?:the\s+)?)?", text[:match.start()], re.I):
        return relation, match
    return None, None


def coordinated_descriptions(prefix: str, entity: str):
    """Expand separately counted descriptions, preserving numeric conjunctions."""
    each = distributive_description(prefix, WORD_TO_TYPE[entity.lower()])
    if each:
        if prefix[each['end']:].strip():
            raise ValueError('An each-color list must stay within one noun phrase; that instruction was skipped.')
        return [{'count':each['count'], 'color':color.group().lower(), 'number':each['number'],
                 'color_match':color, 'offset':0, 'negated':each['negated']} for color in each['colors']]
    numbers = list(NUMBER_RE.finditer(prefix))
    separators = [m for m in re.finditer(r',|\band\b', prefix, re.I)
                  if not any(number.start() <= m.start() < number.end() for number in numbers)]
    if not separators:
        return None
    boundaries = [(0, separators[0].start())]
    boundaries += [(a.end(), b.start()) for a, b in zip(separators, separators[1:])]
    boundaries += [(separators[-1].end(), len(prefix))]
    variants = []
    for start, end in boundaries:
        fragment = prefix[start:end]
        if not fragment.strip():
            continue
        colors = list(COLOR_RE.finditer(fragment))
        count, number = quantity(fragment, entity)
        if len(colors) > 1 or number is None or count is None:
            # A leading conjunction after a previous noun is not ellipsis.
            if len([1 for a, b in boundaries if prefix[a:b].strip()]) < 2:
                return None
            raise ValueError('Coordinated descriptions need an explicit, unambiguous quantity for each group.')
        variants.append({'count': count, 'color': colors[0].group().lower() if colors else None,
                         'number': number, 'color_match': colors[0] if colors else None, 'offset': start,
                         'negated': bool(NEGATION_RE.search(fragment))})
    return variants if len(variants) > 1 else None


def postnoun_attributes(suffix: str, kind: str):
    """Read only adjacent, explicit attributes; return offsets into the suffix.

    Quantities require an appositive marker (of them/in total/altogether).
    Colors map to the existing house-roof/tree-foliage/flower-petal field.
    Never scan through a relation, another subject, or an unsupported phrase.
    """
    result = {'end': 0, 'count': None, 'has_quantity': False, 'number': None, 'number_offset': 0, 'colors': [], 'error': None}
    while True:
        start = result['end']
        total_of = TOTAL_OF_PREFIX_RE.match(suffix, start)
        if total_of:
            qualifier = re.match(r'(?:exactly\s+)?', suffix[total_of.end():], re.I)
            number_start = total_of.end() + qualifier.end()
            number = NUMBER_RE.match(suffix, number_start)
            end = number.end() if number else number_start
            count, _ = quantity(suffix[number_start:end], kind)
            if not number or NEGATION_RE.search(suffix[start:total_of.end()]):
                count = None
            alternative = re.match(r'\s+(?:or|to)\s+', suffix[end:], re.I)
            if alternative:
                second = NUMBER_RE.match(suffix, end + alternative.end())
                end = second.end() if second else end + alternative.end()
                count = None
            if result['has_quantity']:
                result['error'] = 'Multiple post-noun quantities are ambiguous; that object instruction was skipped.'
            result.update(count=count, has_quantity=True, number=number, number_offset=0, end=end)
            continue
        post_quantity = POST_QUANTITY_RE.match(suffix, start)
        if post_quantity and not re.match(r'and\b',post_quantity.group('phrase'),re.I) and all(re.fullmatch(r'[+-]?\d+(?:\.\d+)?', word) or all(part in POST_QUANTITY_WORDS for part in word.split('-')) for word in post_quantity.group('phrase').lower().split()):
            phrase = post_quantity.group('phrase')
            count, number = quantity(phrase, kind)
            if NEGATION_RE.search(phrase) or not number:
                count = None
            if result['has_quantity']:
                result['error'] = 'Multiple post-noun quantities are ambiguous; that object instruction was skipped.'
            result.update(count=count, has_quantity=True, number=number,
                          number_offset=post_quantity.start('phrase'), end=post_quantity.end())
            continue
        color = POST_COLOR_RE.match(suffix, start)
        if color:
            field = next(name for name in ('predicate', 'before', 'after', 'bare') if color.group(name))
            part = color.group('part_before') or color.group('part_after')
            if kind not in COLOR_PARTS or part and part.lower() not in COLOR_PARTS[kind]:
                result['error'] = 'This object color/part has no supported visual mapping; that object instruction was skipped.'
            result['colors'].append((color.group(field).lower(), color.start(field), color.end(field)))
            result['end'] = color.end()
            continue
        # Reject an explicit but unsupported color attribute instead of
        # silently applying its first color or dropping a negation.
        rest = suffix[start:]
        _, relation = relation_in(rest)
        boundary = relation.start() if relation else len(rest)
        next_noun = ENTITY_RE.search(rest)
        if next_noun:
            boundary = min(boundary, next_noun.start())
        attribute = rest[:boundary]
        explicit_attribute = re.match(r'\s*,?\s*(?:with|without|having|whose|that|which|is|are|not)\b', attribute, re.I)
        conflicting_color = result['colors'] and not next_noun and re.match(r'\s*(?:and|or)\s+(?:' + '|'.join(COLORS) + r')\b', attribute, re.I)
        if (explicit_attribute and not next_noun or conflicting_color) and COLOR_RE.search(attribute):
            result['error'] = 'Unsupported, negated or ambiguous post-noun color; that object instruction was skipped.'
        break
    if len({color for color, _, _ in result['colors']}) > 1:
        result['error'] = 'Conflicting post-noun colors; that object instruction was skipped.'
    return result


def post_each_colors(suffix: str, kind: str):
    """Read an adjacent of-each-color list without scanning through another noun."""
    marker = re.match(r'\s+of\s+each\s+colou?r\b\s*[:,]?\s*', suffix, re.I)
    if not marker:
        return None
    word = r'(?:' + '|'.join(COLORS) + r')\b'
    listing = re.match(word + r'(?:\s*(?:,\s*(?:and\s+)?|and\s+)' + word + r')+', suffix[marker.end():], re.I)
    end = marker.end() + listing.end() if listing else marker.end()
    error = None
    colors = list(COLOR_RE.finditer(suffix,marker.end(),end))
    if not listing or kind not in COLOR_PARTS or len({c.group().lower() for c in colors}) != len(colors):
        error = 'Of each color needs a distinct supported color list; that instruction was skipped.'
    tail = re.match(r'\s*(?:or|to)\b|\s*(?:,\s*|and\s+)(?P<next>\w+)', suffix[end:], re.I)
    if tail and (not tail.group('next') or not NUMBER_RE.fullmatch(tail.group('next')) and not ENTITY_RE.fullmatch(tail.group('next'))):
        error = 'Of each color has an ambiguous or unsupported list; that instruction was skipped.'
    return {'end':end, 'colors':colors, 'error':error}


def distributive_description(fragment: str, kind: str):
    """A single explicit quantity distributes over an adjacent color list."""
    prefix = re.match(r'\s*(?:(?:not|no|never|without)\s+)?(?:exactly\s+)?', fragment, re.I)
    number = NUMBER_RE.match(fragment, prefix.end())
    if number is None and re.match(r'(?:\w+\s+)?each\b', fragment[prefix.end():], re.I):
        raise ValueError('Each needs an explicit whole-number quantity; that instruction was skipped.')
    each = re.match(r'\s+each\b\s*(?:of\s+)?', fragment[number.end():], re.I) if number else None
    if not each:
        return None
    start = number.end() + each.end()
    color_word = r'(?:' + '|'.join(COLORS) + r')\b'
    listing = re.match(color_word + r'(?:\s*(?:,\s*(?:and\s+)?|and\s+)' + color_word + r')+', fragment[start:], re.I)
    count, _ = quantity(fragment[:number.end()], kind)
    if not listing or count is None or kind not in COLOR_PARTS:
        raise ValueError('Each needs a valid whole-number count and an explicit supported color list; that instruction was skipped.')
    end = start + listing.end()
    if re.match(r'\s*(?:or|to)\b|\s*(?:,\s*|and\s+)(?:black|brown|gray|grey|cyan)\b', fragment[end:], re.I):
        raise ValueError('An each-color list is ambiguous or unsupported; that instruction was skipped.')
    return {'count':count, 'number':number, 'colors':list(COLOR_RE.finditer(fragment,start,end)),
            'end':end, 'negated':bool(NEGATION_RE.search(fragment[:number.start()]))}


# Fractions of a declared total: halves, thirds, quarters/fourths, fifths, tenths and
# percentages, optionally "the remaining ...". Counts must still come out whole.
FRACTION_UNITS = {"half": 2, "halves": 2, "third": 3, "thirds": 3, "quarter": 4, "quarters": 4, "fourth": 4, "fourths": 4,
                  "fifth": 5, "fifths": 5, "tenth": 10, "tenths": 10}
FRACTION_RE = re.compile(
    r"(?:(?:not|no|never|without)\s+)?(?:(?:the\s+)?remaining\s+)?(?:"
    r"(?P<half>(?:a\s+)?half\b(?!\s+(?:a\s+)?dozen))"
    r"|(?P<percent>\d+(?:\.\d+)?)\s*(?:%|percent\b|per\s+cent\b)"
    r"|(?:(?P<numerator>" + NUMERAL + r"|a|an)[ -]+)?(?P<unit>thirds?|quarters?|fourths?|fifths?|tenths?)\b"
    r")(?:\s+of\s+them\b)?", re.I)


def fraction_ratio(match):
    """(numerator, denominator) for a FRACTION_RE match; numerator is None when unreadable."""
    if match.group("half"):
        return (1, 2)
    if match.group("percent"):
        value = Fraction(match.group("percent")) / 100
        return (value.numerator, value.denominator)
    numerator = (match.group("numerator") or "one").lower()
    count = 1 if numerator in {"a", "an", "one"} else number_value(numerator)
    return (count, FRACTION_UNITS[match.group("unit").lower()])


def continued_descriptions(suffix: str, kind: str):
    """Adjacent count groups can reuse a noun through ones or a relative clause.

    This is noun-type ellipsis for new creations, not an ID reference to old
    objects. Stop before an explicit new noun, verb or placement constraint.
    Returned annotations retain offsets into the unchanged suffix.
    """
    result = {'end': 0, 'descriptions': [], 'highlights': [], 'error': None,
              'first_comma': False, 'first_colon': False, 'first_form': None}
    while connector := re.match(r'\s*(?:[,:]\s*(?:and\s+)?|and\s+)', suffix[result['end']:], re.I):
        start = result['end'] + connector.end()
        try:
            each = distributive_description(suffix[start:], kind)
        except ValueError as exc:
            result.update(end=start, error=str(exc))
            break
        if each:
            if not result['descriptions']:
                result.update(first_comma=connector.group().lstrip().startswith((',', ':')),
                              first_colon=connector.group().lstrip().startswith(':'), first_form='distributive')
            result['descriptions'] += [{'count':each['count'], 'color':c.group().lower(),
                                        'negated':each['negated'], 'remainder':False} for c in each['colors']]
            result['highlights'].append((start + each['number'].start(), start + each['number'].end(), 'quantity'))
            result['highlights'] += [(start+c.start(),start+c.end(),'color') for c in each['colors']]
            result['end'] = start + each['end']
            continue
        inferred = re.match(r'(?:(?:not|no|never|without)\s+)?(?:the\s+(?:rest|remainder)|(?:the\s+)?remaining\s+ones?)\b', suffix[start:], re.I)
        fraction = FRACTION_RE.match(suffix[start:])
        ratio = fraction_ratio(fraction) if fraction else None
        qualifier = re.match(r'(?:(?:not|no|never|without)\s+)?(?:(?:the\s+)?remaining\s+)?(?:exactly\s+)?', suffix[start:], re.I)
        number_start = start + qualifier.end()
        number = NUMBER_RE.match(suffix, number_start) if not inferred and not fraction else None
        if number is None and not inferred and not fraction:
            # Explicit inherited wording without a count is not a new noun.
            unfinished = re.match(
                r'(?:large|small|big|tiny|little)\s+ones\b|(?:that|which|whose)\b|(?:'
                + '|'.join(COLORS) + r')\b(?=\s*(?:and\b|,|$))', suffix[start:], re.I)
            if unfinished:
                result.update(end=start + unfinished.end(), error='An inherited noun group needs an explicit quantity; that object instruction was skipped.')
            break
        cursor = start + (inferred or fraction).end() if inferred or fraction else number.end()
        of = re.match(r'\s+of\b', suffix[cursor:], re.I)
        if of and number and (number.group('group') or number.group('half')):
            cursor += of.end()
        colors = []
        while modifier := GROUP_MODIFIER_RE.match(suffix, cursor):
            if modifier.group(1).lower() in COLORS:
                colors.append((modifier.group(1).lower(), modifier.start(1), modifier.end(1)))
            cursor = modifier.end()
        space = re.match(r'\s*', suffix[cursor:])
        if ENTITY_RE.match(suffix, cursor + space.end()):
            break  # An explicit next noun is handled by the main mention loop.
        ellipsis = re.match(r'\s+ones?\b', suffix[cursor:], re.I)
        attribute_start = cursor + ellipsis.end() if ellipsis else cursor
        attributes = postnoun_attributes(suffix[attribute_start:], kind)
        end = attribute_start + attributes['end']
        if ellipsis or inferred or fraction:
            form = 'ones'
        elif attributes['colors']:
            form = 'relative' if re.match(r'\s*(?:that|which|whose)\b', suffix[cursor:], re.I) else 'part'
        elif colors:
            form = 'predicate'
        else:
            # Detect malformed inherited clauses without looking through
            # another explicit noun and accidentally creating its landmark.
            marker = re.match(r'\s*(?:that|which|whose|with|ones?)\b', suffix[cursor:], re.I)
            invalid = re.match(r'\s*(?:or|and|to)\s+[^,;]*?\bones\b', suffix[cursor:], re.I)
            if marker or invalid or attributes['error']:
                stop = cursor + (marker or invalid).end() if marker or invalid else cursor
                result.update(end=stop, error='An inherited group needs an unambiguous count and a supported description; that object instruction was skipped.')
            break
        count, _ = quantity(suffix[start:number.end()], kind) if number else (None, None)
        if count is None and not inferred and not fraction or len(colors) > 1:
            result.update(end=end, error='An inherited noun group needs explicit, unambiguous counts and colors; that object instruction was skipped.')
            break
        color = colors[0][0] if colors else None
        if attributes['error'] or attributes['has_quantity'] and attributes['count'] != count or attributes['colors'] and color and color != attributes['colors'][-1][0]:
            result.update(end=end, error=attributes['error'] or 'Conflicting attributes in an inherited noun group; that object instruction was skipped.')
            break
        if re.match(r'\s*(?:or|to)\b|\s*and\s+(?:' + '|'.join(COLORS) + r')\b', suffix[end:], re.I):
            result.update(end=end, error='An inherited group has ambiguous colors; that object instruction was skipped.')
            break
        if attributes['colors']:
            color = attributes['colors'][-1][0]
        negated = bool(NEGATION_RE.search(suffix[start:number.start() if number else cursor]))
        remainder = inferred or (re.search(r'\bremaining\b', suffix[start:number.start()], re.I) if number else None)
        if not result['descriptions']:
            result['first_comma'] = connector.group().lstrip().startswith((',', ':'))
            result['first_colon'] = connector.group().lstrip().startswith(':')
            result['first_form'] = form
        result['descriptions'].append({'count':count, 'color':color, 'negated':negated, 'remainder':bool(remainder), 'fraction':ratio})
        if remainder:
            result['highlights'].append((start + remainder.start(), start + remainder.end(), 'quantity'))
        if number:
            result['highlights'].append((number.start(), number.end(), 'quantity'))
        if fraction:
            result['highlights'].append((start + fraction.start(), start + fraction.end(), 'quantity'))
        result['highlights'] += [(a, b, 'color') for _, a, b in colors]
        result['highlights'] += [(attribute_start + a, attribute_start + b, 'color') for _, a, b in attributes['colors']]
        if ellipsis:
            word = re.search(r'\bones?\b', ellipsis.group(), re.I)
            result['highlights'].append((cursor + word.start(), cursor + word.end(), 'object'))
        result['end'] = end
    return result
