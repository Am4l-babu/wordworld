"""Explainable lexical grounding; spaCy annotates grammar, not world actions."""
from __future__ import annotations

import re
from typing import Any
from .references import ReferenceContext, UnresolvedReference

try:
    import spacy
except ImportError:
    spacy = None

NLP = None
NLP_STATUS = "rules"
if spacy is not None:
    try:
        NLP = spacy.load("en_core_web_sm")
        NLP_STATUS = "spacy"
    except OSError:
        NLP = spacy.blank("en")
        NLP_STATUS = "spacy-tokenizer"

ALIASES = {
    "house": ["house", "houses", "home", "homes", "cottage", "cottages", "hut", "huts", "cabin", "cabins", "village", "villages", "town", "towns"],
    "tree": ["tree", "trees", "forest", "forests", "woods", "woodland", "woodlands"],
    "lake": ["lake", "lakes", "pond", "ponds"],
    "river": ["river", "rivers", "stream", "streams", "creek", "creeks"],
    "bridge": ["bridge", "bridges"],
    "road": ["road", "roads", "path", "paths", "trail", "trails", "street", "streets"],
    "flower": ["flower", "flowers", "garden", "gardens", "blossom", "blossoms"],
    "mountain": ["mountain", "mountains", "hill", "hills", "peak", "peaks"],
    "tower": ["tower", "towers", "lighthouse", "lighthouses"],
    "castle": ["castle", "castles", "fortress", "fortresses"],
    "rock": ["rock", "rocks", "stone", "stones", "boulder", "boulders"],
}
WORD_TO_TYPE = {word: kind for kind, words in ALIASES.items() for word in words}
ENTITY_RE = re.compile(r"\b(" + "|".join(sorted(map(re.escape, WORD_TO_TYPE), key=len, reverse=True)) + r")\b", re.I)
PRONOUN_RE = re.compile(r"\b(?:it|them)\b", re.I)
MENTION_RE = re.compile(ENTITY_RE.pattern + r"|\b(?:it|them)\b", re.I)
NUMBER_VALUES = dict(zip(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty thirty forty fifty sixty seventy eighty ninety".split(),
    list(range(20)) + list(range(20, 100, 10)),
))
COUNT_WORDS = {**NUMBER_VALUES, "a": 1, "an": 1, "couple": 2, "few": 3, "several": 4}
UNITS = "one|two|three|four|five|six|seven|eight|nine"
BASE_NUMBER = rf"(?:(?:twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)(?:[- ](?:{UNITS}))?|{'|'.join(list(NUMBER_VALUES)[:20])})"
CARDINAL = rf"(?:(?:{BASE_NUMBER})\s+(?:hundred|thousand)(?:\s+(?:and\s+)?{BASE_NUMBER})?|hundred|thousand|{BASE_NUMBER})"
NUMERAL = rf"(?:[+-]?\d+(?:\.\d+)?|{CARDINAL})"
NUMBER_RE = re.compile(
    rf"(?<!\w)(?:(?P<half>half\s+(?:a\s+)?dozen)|(?:(?P<multiplier>{NUMERAL}|a|an)\s+)?(?P<group>dozens?|pairs?|couples?)|(?P<number>{NUMERAL})|(?P<approx>few|several)|(?P<article>a|an))\b", re.I
)
UNKNOWN_QUANTITY_WORDS = {'many', 'some', 'lots', 'numerous', 'million', 'billion', 'quarter'}
UNKNOWN_QUANTITY_RE = re.compile(r"\b(?:" + '|'.join(sorted(UNKNOWN_QUANTITY_WORDS)) + r")\b", re.I)
COLORS = ["red", "blue", "yellow", "pink", "purple", "green", "orange", "white"]
COLOR_RE = re.compile(r"\b(" + "|".join(COLORS) + r")\b", re.I)
RELATION_PATTERNS = [
    ("left", r"\b(?:to the left of|left of|west of)\b"),
    ("right", r"\b(?:to the right of|right of|east of)\b"),
    ("above", r"\b(?:above|behind|north of|at the back of)\b"),
    ("below", r"\b(?:below|in front of|south of)\b"),
    ("near", r"\b(?:beside|next to|near|by|close to|around the edge of|around|along)\b"),
    ("between", r"\bbetween\b"),
    ("across", r"\b(?:across|over|spanning|crossing)\b"),
    ("inside", r"\b(?:inside|within|in the middle of|in the center of)\b"),
]
ADD_PATTERN = r"add|build|create|place|put|plant|grow|make|draw|generate|insert|show|there (?:is|are)|i want|give me"
REMOVE_PATTERN = r"remove|delete|erase|destroy|cut down|clear away|get rid of"
RESET_PATTERN = r"reset|clear (?:everything|the world|the map)|start over|new world"
PRESERVE_PATTERN = r"keep|leave|preserve|retain|protect|avoid"
OPERATION_RE = re.compile(rf"\b(?P<remove>{REMOVE_PATTERN})\b|\b(?P<reset>{RESET_PATTERN})\b|\b(?P<preserve>{PRESERVE_PATTERN})\b|\b(?P<add>{ADD_PATTERN})\b", re.I)
WEATHER_SWITCH_PATTERN = r'(?:turn|switch)\s+(?:(?:the\s+)?(?:rain|snow)\s+(?:on|off)|(?:on|off)\s+(?:the\s+)?(?:rain|snow))'
WEATHER_SWITCH_RE = re.compile(r'\b(?:turn|switch)\s+(?:(?:the\s+)?(?P<before>rain|snow)\s+(?P<after_state>on|off)|(?P<state>on|off)\s+(?:the\s+)?(?P<after>rain|snow))\b', re.I)
WEATHER_STOP_PATTERN = r'(?:stop|end)\s+(?:the\s+)?(?:rain|snow|storm|shower|raining|snowing)'
WEATHER_STOP_RE = re.compile(r'\b' + WEATHER_STOP_PATTERN + r'\b', re.I)
CLAUSE_BREAK_RE = re.compile(
    rf"[;!?,]+|(?<!\d)\.|\.(?!\d)|\b(?:and then|then)\b|\b(?:and|but)\s+(?=(?:(?:do not|don't|never)\s+)?(?:{ADD_PATTERN}|{REMOVE_PATTERN}|{RESET_PATTERN}|{PRESERVE_PATTERN}|{WEATHER_SWITCH_PATTERN}|{WEATHER_STOP_PATTERN})\b)", re.I
)
NEGATION_RE = re.compile(r"\b(?:no|not|don't|do not|never|without|can't|cannot|shouldn't|mustn't|won't|wouldn't|couldn't)\b", re.I)
MATCH_TRANSLATION = str.maketrans({'\u2018': "'", '\u2019': "'", '\u02bc': "'", '\u2212': '-', '\u2010': '-', '\u2011': '-', '\u2013': '-'})
MAX_PER_COMMAND = 16


def tokenize(text: str) -> list[dict[str, Any]]:
    if NLP is None:
        return [{"text": m.group(), "pos": "WORD", "dep": "", "lemma": m.group().lower(),
                 "start": m.start(), "end": m.end(), "head": None, "head_start": None}
                for m in re.finditer(r"[\w']+|[^\s\w]", text)][:100]
    return [{"text": t.text, "pos": t.pos_ or "TOKEN", "dep": t.dep_ or "", "lemma": t.lemma_ or t.text.lower(),
             "start": t.idx, "end": t.idx + len(t.text),
             "head": t.head.text if t.dep_ else None, "head_start": t.head.idx if t.dep_ else None}
            for t in NLP(text) if not t.is_space][:100]


def clauses(text: str):
    """Keep original offsets while separating explicit intents and list commas."""
    start, continuation = 0, False
    for separator in CLAUSE_BREAK_RE.finditer(text):
        prefix = text[start:separator.start()]
        # A comma ending an initial location phrase belongs to the following
        # command, not to a separate implicit object-creation clause.
        if separator.group().startswith(',') and leading_relation(prefix)[0] and not OPERATION_RE.search(prefix):
            continue
        operation = OPERATION_RE.search(prefix)
        if separator.group().startswith(',') and operation and operation.lastgroup == 'add' and not ENTITY_RE.search(prefix) and NUMBER_RE.search(prefix):
            following = text[separator.end():]
            noun = ENTITY_RE.search(following)
            if noun and not OPERATION_RE.search(following[:noun.start()]):
                continue
        nouns = list(ENTITY_RE.finditer(prefix))
        if separator.group().startswith(',') and nouns:
            # Commas inside one distributive color list are not new clauses.
            noun = nouns[-1]
            kind = WORD_TO_TYPE[noun.group().lower()]
            source_attributes = postnoun_attributes(text[noun.end():], kind)
            group_start = noun.end() + source_attributes['end']
            source_groups = continued_descriptions(text[group_start:], kind)
            if group_start + source_groups['end'] > separator.start():
                continue
            shared_tail = re.match(r'\s*all\s+(?:(?:not|no|without)\s+)?', text[separator.end():], re.I)
            if source_groups['descriptions'] and shared_tail and leading_relation(text[separator.end()+shared_tail.end():])[0]:
                continue  # One same-noun collection owns this shared placement.
            # Appositive attributes belong to the preceding noun, including
            # the 'them' in a quantity, rather than a new command/reference.
            attributes = postnoun_attributes(text[separator.start():], WORD_TO_TYPE[nouns[-1].group().lower()])
            groups = continued_descriptions(text[separator.start():], WORD_TO_TYPE[nouns[-1].group().lower()])
            if attributes['end'] or groups['end']:
                continue
        if text[start:separator.start()].strip():
            yield start, text[start:separator.start()], continuation
        start = separator.end()
        continuation = separator.group().startswith(',')
    if text[start:].strip():
        yield start, text[start:], continuation


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


PASSIVE_ADVERBS = r'(?:(?:already|recently|just|newly|previously|freshly)\s+){0,2}'
POST_COLOR_RE = re.compile(
    r'\s*,?\s*(?:'
    r'(?:(?:that|which)\s+)?(?:is|are)\s+(?P<predicate>' + '|'.join(COLORS) + r')\b|'
    r'(?:with|having|(?:that|which)\s+(?:has|have))\s+(?:(?:a|an|the)\s+)?(?P<before>' + '|'.join(COLORS) + r')\s+(?P<part_before>roofs?|leaves|foliage|petals?)\b|'
    r'(?:whose|with|having|(?:that|which)\s+(?:has|have))\s+(?:(?:a|an|the)\s+)?(?P<part_after>roofs?|leaves|foliage|petals?)\s+'
    r'(?:(?:(?:that|which)\s+)?(?:is|are)\s+' + PASSIVE_ADVERBS + r'(?:(?:painted|colou?red)\s+)?|(?:(?:that|which)\s+)?(?:will|shall)\s+be\s+' + PASSIVE_ADVERBS + r'(?:painted|colou?red)\s+|(?:(?:that|which)\s+)?(?:has|have|had)\s+' + PASSIVE_ADVERBS + r'been\s+' + PASSIVE_ADVERBS + r'(?:painted|colou?red)\s+|(?:painted|colou?red)\s+)'
    r'(?P<after>' + '|'.join(COLORS) + r')\b|'
    r'(?:in\s+)?(?P<bare>' + '|'.join(COLORS) + r')\b)', re.I)
COLOR_PARTS = {'house': {'roof', 'roofs'}, 'tree': {'leaves', 'foliage'}, 'flower': {'petal', 'petals'}}
POST_QUANTITY_RE = re.compile(r'\s*,?\s*(?P<phrase>[\w+.-]+(?:\s+[\w+.-]+){0,7}?)\s+(?:of\s+them|in\s+(?:total|all)|total|altogether)\b', re.I)
TOTAL_OF_PREFIX_RE = re.compile(r'\s*[, :]?\s*(?:(?:not|no|never|without)\s+)?(?:a|the)\s+total\s+of\s+', re.I)
POST_QUANTITY_WORDS = set(COUNT_WORDS) | {'exactly','dozen','dozens','pair','pairs','couples','half','of','hundred','thousand','and','or','to','not'} | UNKNOWN_QUANTITY_WORDS


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


GROUP_SIZES = {'small','large','little','tiny','cozy','big','tall','short'}
GROUP_MODIFIER_RE = re.compile(r'\s+(' + '|'.join(sorted(GROUP_SIZES | set(COLORS))) + r')\b', re.I)


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
        fraction = re.match(r'(?:(?:not|no|never|without)\s+)?(?:a\s+)?half\b(?!\s+(?:a\s+)?dozen)(?:\s+of\s+them\b)?', suffix[start:], re.I)
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
        result['descriptions'].append({'count':count, 'color':color, 'negated':negated, 'remainder':bool(remainder), 'fraction':bool(fraction)})
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


def parse(text: str) -> dict[str, Any]:
    if len(text) > 1400:
        raise ValueError("Please keep commands under 1,400 characters.")
    if not text.strip():
        raise ValueError("Enter a world-building instruction.")
    actions: list[dict[str, Any]] = []
    highlights: list[dict[str, Any]] = []
    warnings: list[str] = []
    references = ReferenceContext()
    resolutions, bindings = [], []

    def mark(start: int, end: int, role: str):
        highlight = {"text": text[start:end], "start": start, "end": end, "role": role}
        if highlight not in highlights:
            highlights.append(highlight)

    def mark_reference(match, offset, groups):
        mark(offset + match.start(), offset + match.end(), 'reference')
        resolutions.append({'text': text[offset + match.start():offset + match.end()],
                            'start': offset + match.start(), 'end': offset + match.end(),
                            'objects': [{'type': g.type, 'count': g.count} for g in groups]})

    def read_landmarks(clause, relation, relation_end, found, first, offset):
        if first >= len(found):
            return [], first, []
        target, consumed = found[first], first
        target_prefix = clause[relation_end:target.start()]
        if NEGATION_RE.search(target_prefix):
            return [], consumed, []
        if PRONOUN_RE.fullmatch(target.group()):
            try:
                groups = references.resolve(target.group())
                total = sum(group.count for group in groups)
                required = 2 if relation == 'between' else 1
                if total != required:
                    raise UnresolvedReference(f"'{target.group()}' needs exactly {required} object(s) for this spatial relation.")
                targets = [group.type for group in groups for _ in range(group.count)]
                mark_reference(target, offset, groups)
                return targets, consumed, groups
            except UnresolvedReference as exc:
                warnings.append(str(exc))
                return [], consumed, []
        targets = [WORD_TO_TYPE[target.group().lower()]]
        mark(offset + target.start(), offset + target.end(), "landmark")
        if relation == "between":
            target_count, target_number = quantity(target_prefix, target.group())
            if target_number:
                mark(offset + relation_end + target_number.start(), offset + relation_end + target_number.end(), "quantity")
            connector = clause[target.end():found[consumed + 1].start()] if consumed + 1 < len(found) else ""
            if target_number and target_count == 2:
                targets.append(targets[0])
            elif target_count == 1 and re.search(r"\band\b", connector) and not OPERATION_RE.search(connector):
                consumed += 1
                second = found[consumed]
                second_count, _ = quantity(connector, second.group())
                if second_count == 1:
                    targets.append(WORD_TO_TYPE[second.group().lower()])
                mark(offset + second.start(), offset + second.end(), "landmark")
            elif not target_number and target.group().lower().endswith('s') and target.group().lower() not in {'fortress', 'woods'}:
                targets.append(targets[0])
        return targets, consumed, []

    inherited_intent, inherited_negated = "add", False
    # One code point maps to one code point: original UI spans stay exact.
    for offset, clause, continuation in clauses(text.translate(MATCH_TRANSLATION)):
        introduced_in_clause = False
        if not continuation:
            inherited_intent, inherited_negated = "add", False
        operation = OPERATION_RE.search(clause)
        introduced_in_clause = bool(continuation and not operation and inherited_intent == 'add' and references.groups)
        if operation:
            inherited_negated = bool(NEGATION_RE.search(clause[:operation.start()]))
        elif re.match(r"^\s*(?:and\s+)?(?:no|not|without|never|don't|do not)\b", clause, re.I) and ENTITY_RE.search(clause):
            inherited_negated = True
        if inherited_negated:
            warnings.append("Skipped a negated instruction; no objects were changed for that clause.")
            continue
        if operation:
            mark(offset + operation.start(), offset + operation.end(), "intent")
        if operation and operation.lastgroup == "reset":
            actions.append({"action": "reset"})
            references.groups = []
            inherited_intent = "add"
            continue
        intent = operation.lastgroup if operation else inherited_intent
        if operation:
            inherited_intent = intent
        if intent == "preserve":
            for entity in ENTITY_RE.finditer(clause):
                mark(offset + entity.start(), offset + entity.end(), "protected")
            warnings.append("Preserved referenced objects; no creation or removal was applied for that clause.")
            continue

        # Choose clear-weather phrases before their embedded rain/snow words.
        time = re.search(r"\b(night|nighttime|moonlight|after dark|midnight|dark sky|day|daytime|daylight|dawn|sunny|sunshine|morning|sunlight)\b", clause, re.I)
        if time and not NEGATION_RE.search(clause[:time.start()]):
            value = "night" if time.group().lower() in {"night", "nighttime", "moonlight", "after dark", "midnight", "dark sky"} else "day"
            actions.append({"action": "setting", "key": "time", "value": value})
            mark(offset + time.start(), offset + time.end(), "setting")
        weather_switch = WEATHER_SWITCH_RE.search(clause)
        weather_stop = WEATHER_STOP_RE.search(clause)
        weather_control = weather_switch or weather_stop
        if weather_control:
            if NEGATION_RE.search(clause[:weather_control.start()]):
                warnings.append('Skipped a negated weather control; weather was unchanged.')
            else:
                state = (weather_switch.group('state') or weather_switch.group('after_state')).lower() if weather_switch else 'off'
                value = 'clear' if state == 'off' else (weather_switch.group('before') or weather_switch.group('after')).lower()
                actions.append({'action':'setting', 'key':'weather', 'value':value})
                mark(offset+weather_control.start(),offset+weather_control.end(),'setting')
        for value, pattern in [] if weather_control else [
            ("clear", r"\b(?:clear weather|(?:no|not|without) (?:rain|rainy|raining|snow|snowy|snowing))\b"),
            ("rain", r"\b(?:rain|rainy|raining|shower|storm)\b"),
            ("snow", r"\b(?:snow|snowy|snowing|winter)\b"),
        ]:
            weather = re.search(pattern, clause, re.I)
            if weather and (value == "clear" or not NEGATION_RE.search(clause[:weather.start()])):
                actions.append({"action": "setting", "key": "weather", "value": value})
                mark(offset + weather.start(), offset + weather.end(), "setting")
                break

        entities = list(MENTION_RE.finditer(clause))
        front_relation, front_match = leading_relation(clause)
        front_targets = []
        front_groups = []
        if operation and front_match and front_match.end() <= operation.start():
            landmarks = [entity for entity in entities if entity.end() <= operation.start()]
            front_targets, consumed, front_groups = read_landmarks(clause, front_relation, front_match.end(), landmarks, 0, offset)
            mark(offset + front_match.start(), offset + front_match.end(), "spatial_relation")
            if not front_targets or front_relation == 'between' and len(front_targets) != 2 or consumed != len(landmarks) - 1:
                warnings.append("Could not resolve the initial location phrase; no objects were changed for that instruction.")
                continue
        else:
            front_relation = None
        if operation:
            entities = [entity for entity in entities if entity.start() >= operation.end()]
        elif entities:
            # Bare noun phrases remain convenient, but unsupported verbs and
            # factual/context statements must never imply an add operation.
            words = set(re.findall(r"[\w']+", clause[:entities[0].start()].lower()))
            modifiers = set(COUNT_WORDS) | set(COLORS) | {"exactly", "the", "my", "your", "please", "and", "or", "with", "small", "large", "little", "tiny", "cozy", "big", "dozen", "dozens", "pair", "pairs", "half", "of", "hundred", "thousand"}
            if any(word not in modifiers and not word.isdigit() for word in words):
                warnings.append("Skipped a context-only or unsupported instruction; use an explicit add/build/plant verb to create objects.")
                continue
        i, cursor = 0, operation.end() if operation else 0
        while i < len(entities):
            entity = entities[i]
            prefix = clause[cursor:entity.start()]
            count, number = quantity(prefix, entity.group())
            if PRONOUN_RE.fullmatch(entity.group()):
                # The 'it' in a time/weather instruction is not an object reference.
                if intent == 'add' and (time or re.search(r'\b(?:rain|snow|weather|raining|snowing)\b', clause, re.I)):
                    cursor, i = entity.end(), i + 1
                    continue
                next_start = entities[i + 1].start() if i + 1 < len(entities) else len(clause)
                if relation_in(clause[entity.end():next_start])[0]:
                    warnings.append('Spatially qualified object-pronoun subjects are not supported; that instruction was skipped.')
                    cursor, i = len(clause), len(entities)
                    continue
                if intent != 'remove' or NEGATION_RE.search(prefix) or count is None or count == 0:
                    warnings.append('Object pronouns can be removal subjects or spatial landmarks; no object was created from this reference.')
                    if intent != 'remove':
                        cursor, i = len(clause), len(entities)
                        continue
                else:
                    try:
                        groups, removals, notice = references.removals(entity.group(), count if number else None)
                        mark_reference(entity, offset, groups)
                        if notice:
                            warnings.append(notice)
                        for kind, amount in removals:
                            bindings.append({'action_index': len(actions), 'remove_from': [g.action_index for g in groups if g.type == kind]})
                            actions.append({'action': 'remove', 'type': kind, 'count': amount})
                            references.consume(kind, amount)
                    except UnresolvedReference as exc:
                        warnings.append(str(exc))
                cursor, i = entity.end(), i + 1
                continue
            colors = list(COLOR_RE.finditer(prefix))
            color = colors[-1] if colors else None
            if re.search(r'\bones\b', prefix, re.I):
                # An unsupported inherited subject followed by a placement
                # phrase must not turn its landmark into a new source noun.
                mark(offset + entity.start(), offset + entity.end(), 'landmark')
                warnings.append('An inherited noun after a placement or new verb needs an explicit source noun; its landmark was not created.')
                cursor, i = entity.end(), i + 1
                continue
            try:
                variants = coordinated_descriptions(prefix, entity.group())
            except ValueError as exc:
                warnings.append(str(exc))
                variants = []
            kind = WORD_TO_TYPE[entity.group().lower()]
            attributes = postnoun_attributes(clause[entity.end():], kind)
            attribute_error = attributes['error']
            if attributes['has_quantity']:
                post_count = attributes['count']
                if variants is not None or number and not number.group('article') and count != post_count:
                    attribute_error = 'Conflicting prefix and post-noun quantities; that object instruction was skipped.'
                count = post_count
            post_colors = attributes['colors']
            conflicting_color = bool(post_colors) and (
                variants is not None and any(v['color'] not in {None, post_colors[-1][0]} for v in variants)
                or variants is None and color and color.group().lower() != post_colors[-1][0])
            if conflicting_color:
                attribute_error = 'Conflicting prefix and post-noun colors; that object instruction was skipped.'
            elif post_colors and variants:
                variants = [{**v, 'color': post_colors[-1][0]} for v in variants]
            group_start = entity.end() + attributes['end']
            continued = continued_descriptions(clause[group_start:], kind)
            if continued['descriptions'] and not attributes['end']:
                # The adjacent group reader, rather than the scalar attribute
                # reader, owns negations/colors inside a counted continuation.
                attribute_error = None
            if continued['error']:
                attribute_error = continued['error']
            # Appositive descriptions replace a bare noun's implicit default.
            # With an explicit total, relative/part/predicate descriptions
            # partition that total. Count agreement also disambiguates ones.
            declared_total = bool(attributes['has_quantity'] or number and (
                not number.group('article') or quantity('', entity.group())[0] == 1))
            fractions = [d for d in continued['descriptions'] if d.get('fraction')]
            if fractions:
                if not declared_total or count is None or count % 2 or not continued['first_comma']:
                    attribute_error = 'Half groups need an explicit even whole-number total and a partition; that instruction was skipped.'
                else:
                    for description in fractions:
                        description['count'] = count // 2
            group_total = sum(d['count'] for d in continued['descriptions'] if not d['negated'] and d['count'] is not None)
            partition = bool(continued['descriptions'] and continued['first_comma'] and (not post_colors or continued['first_colon']) and (
                not declared_total or continued['first_form'] != 'ones' or group_total == count or continued['first_colon'] or any(d.get('remainder') for d in continued['descriptions'])))
            remainders = [j for j,d in enumerate(continued['descriptions']) if d.get('remainder')]
            if remainders and (not partition or not declared_total or remainders != [len(continued['descriptions'])-1]):
                attribute_error = 'A remaining group needs a declared total and must be the final partition group; that instruction was skipped.'
            inferred_groups = [d for d in continued['descriptions'] if d['count'] is None and d.get('remainder')]
            if inferred_groups:
                if attribute_error or count is None or count < group_total or inferred_groups[0]['negated']:
                    attribute_error = attribute_error or 'Cannot infer a non-negative remainder from that total; that instruction was skipped.'
                else:
                    inferred_groups[0]['count'] = count - group_total
                    group_total = count
            if partition:
                if variants is not None or NEGATION_RE.search(prefix):
                    attribute_error = 'A negated or already coordinated source cannot supply a counted partition; that instruction was skipped.'
                elif declared_total and count != group_total:
                    attribute_error = 'Partition counts do not match the declared total; that object instruction was skipped.'
                if color or post_colors:
                    shared_color = post_colors[-1][0] if post_colors else color.group().lower()
                    if any(d['color'] not in {None, shared_color} for d in continued['descriptions']):
                        attribute_error = 'Partition colors conflict with the source color; that object instruction was skipped.'
                    continued['descriptions'] = [{**d, 'color': d['color'] or shared_color} for d in continued['descriptions']]
            subject_end = group_start + continued['end']
            after_subject = i + 1
            while after_subject < len(entities) and entities[after_subject].start() < subject_end:
                after_subject += 1
            next_start = entities[after_subject].start() if after_subject < len(entities) else len(clause)
            gap = clause[subject_end:next_start]
            relation, rel_match = relation_in(gap)
            consumed = after_subject - 1
            targets = []
            target_groups = []
            unsupported_connection = after_subject < len(entities) and not relation and not NEGATION_RE.search(gap) and not re.match(r'\s*(?:and|with)\b', gap, re.I)
            negated_relation = rel_match is not None and bool(NEGATION_RE.search(gap[:rel_match.start()]))
            if unsupported_connection:
                mark(offset + entities[after_subject].start(), offset + entities[after_subject].end(), 'landmark')
                consumed = len(entities) - 1
            if relation and after_subject < len(entities):
                targets, consumed, target_groups = read_landmarks(clause, relation, subject_end + rel_match.end(), entities, after_subject, offset)
                # Multi-hop references are outside the grammar: never turn a
                # chained landmark into an unintended creation.
                while consumed + 1 < len(entities):
                    chain = clause[entities[consumed].end():entities[consumed + 1].start()]
                    chain_relation, _ = relation_in(chain)
                    if not chain_relation or re.search(r"\b(?:and|with)\b", chain, re.I):
                        break
                    consumed += 1
                    chained = entities[consumed]
                    mark(offset + chained.start(), offset + chained.end(), "landmark")
                    warnings.append("Chained landmark relations are not resolved; only the first spatial relation was used.")
            conflicting_relations = bool(front_relation and relation)
            if front_relation and not relation:
                relation, targets = front_relation, front_targets
                target_groups = front_groups
            mark(offset + entity.start(), offset + entity.end(), "object")
            if number and variants is None:
                mark(offset + cursor + number.start(), offset + cursor + number.end(), "quantity")
            if color and variants is None:
                mark(offset + cursor + color.start(), offset + cursor + color.end(), "color")
            if attributes['number']:
                post_number = attributes['number']
                base = offset + entity.end() + attributes['number_offset']
                mark(base + post_number.start(), base + post_number.end(), 'quantity')
            for _, start, end in post_colors:
                mark(offset + entity.end() + start, offset + entity.end() + end, 'color')
            for start, end, role in continued['highlights']:
                mark(offset + group_start + start, offset + group_start + end, role)
            for variant in variants or []:
                base = offset + cursor + variant['offset']
                mark(base + variant['number'].start(), base + variant['number'].end(), 'quantity')
                if variant['color_match']:
                    mark(base + variant['color_match'].start(), base + variant['color_match'].end(), 'color')
            if rel_match:
                mark(offset + subject_end + rel_match.start(), offset + subject_end + rel_match.end(), "spatial_relation")

            if attribute_error:
                warnings.append(attribute_error)
            elif unsupported_connection:
                warnings.append('Unsupported connection between object nouns; that object instruction was skipped instead of creating its landmark.')
            elif negated_relation:
                warnings.append('Negated spatial constraints are not supported; that object instruction was skipped.')
            elif conflicting_relations:
                warnings.append("Multiple placement constraints in one noun phrase are not supported; that object instruction was skipped.")
            elif variants == []:
                pass
            elif count is None and variants is None:
                warnings.append(f"Skipped {kind}: specify an unambiguous non-negative whole-number quantity.")
            elif variants is None and not continued['descriptions'] and (NEGATION_RE.search(prefix) or count == 0):
                warnings.append(f"Skipped negated or zero-count {kind} instruction.")
            elif relation and (not targets or relation == "between" and len(targets) != 2):
                warnings.append("A spatial instruction needs named landmarks; use 'between two houses' or 'between the house and the lake'.")
            elif intent == "remove" and relation:
                warnings.append("Spatially filtered removal is not supported; specify a type and quantity to remove.")
            elif intent == 'remove' and (variants is not None or continued['descriptions']):
                warnings.append('Coordinated removal descriptions are not supported; specify an object type and quantity.')
            elif intent == "remove":
                amount = min(count, MAX_PER_COMMAND) if number or attributes['has_quantity'] else 'all'
                actions.append({"action": "remove", "type": kind, "count": amount})
                references.consume(kind, amount)
            else:
                final_color = post_colors[-1][0] if post_colors else color.group().lower() if color else None
                descriptions = variants if variants is not None else [{'count': count, 'color': final_color, 'negated': bool(NEGATION_RE.search(prefix))}]
                if partition:
                    descriptions = []
                descriptions = descriptions + continued['descriptions']
                for description in descriptions:
                    if description['negated'] or description['count'] == 0:
                        warnings.append(f'Skipped a negated or zero-count {kind} group.')
                        continue
                    action = {"action": "add", "type": kind, "count": min(description['count'], MAX_PER_COMMAND), "color": description['color']}
                    if relation:
                        action.update(relation=relation, target=targets[0])
                        if relation == "between":
                            action["targets"] = targets
                    if target_groups:
                        bindings.append({'action_index': len(actions), 'target_from': [g.action_index for g in target_groups]})
                    references.introduce(kind, action['count'], len(actions), new_clause=not introduced_in_clause)
                    introduced_in_clause = True
                    actions.append(action)
                    if description['count'] > MAX_PER_COMMAND:
                        warnings.append(f'Limited {kind} quantity to {MAX_PER_COMMAND}.')
            if count is not None and count > MAX_PER_COMMAND:
                warnings.append(f"Limited {kind} quantity to {MAX_PER_COMMAND}.")
            cursor = max(subject_end, entities[consumed].end())
            i = consumed + 1
            if relation and consumed >= after_subject and ENTITY_RE.fullmatch(entities[consumed].group()):
                # Landmark attributes cannot become the next subject's prefix.
                landmark_kind = WORD_TO_TYPE[entities[consumed].group().lower()]
                landmark_attributes = postnoun_attributes(clause[cursor:], landmark_kind)
                if landmark_attributes['end']:
                    cursor += landmark_attributes['end']
                    warnings.append('Landmark attributes are not used as filters; placement uses the named object type.')
                    while i < len(entities) and entities[i].start() < cursor:
                        i += 1

        if not entities and not time and not re.search(r"\b(?:rain|snow|weather|raining|snowing|rainy|snowy|winter|storm|shower)\b", clause, re.I):
            warnings.append("No supported object or setting found in one clause. Name an object explicitly; pronoun references are not resolved.")

    for ellipsis in re.finditer(r'\bones\b', text, re.I):
        if not any(h['role'] == 'object' and h['start'] == ellipsis.start() for h in highlights):
            warnings.append('Could not resolve an inherited noun outside an adjacent creation group; use an explicit object noun.')
    if len(actions) > 20:
        actions = actions[:20]
        warnings.append("Limited this command to 20 actions.")
    return {
        "text": text,
        "actions": actions,
        "tokens": tokenize(text),
        "highlights": sorted(highlights, key=lambda h: (h["start"], h["end"])),
        "warnings": list(dict.fromkeys(warnings)),
        "message": f"Understood {len(actions)} instruction{'s' if len(actions) != 1 else ''}." if actions else "No scene changes were applied. Check the parser notices." if warnings else "Try describing a house, trees, a lake, a bridge, or ask for night/rain.",
        "model": NLP_STATUS,
        "grounding": "rules",
        "resolutions": resolutions,
        "bindings": bindings,
        "supported_objects": list(ALIASES),
    }
