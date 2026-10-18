"""Explainable lexical grounding; spaCy annotates grammar, not world actions."""
from __future__ import annotations

import re
from typing import Any

from .lexicon import (
    ALIASES, CLAUSE_BREAK_RE, COLORS, COLOR_RE, COUNT_WORDS, ENTITY_RE,
    MATCH_TRANSLATION, MAX_PER_COMMAND, MENTION_RE, NEGATION_RE, NUMBER_RE,
    OPERATION_RE, PRONOUN_RE, SINGULAR_NOUNS, WEATHER_STOP_RE, WEATHER_SWITCH_RE,
    WORD_TO_TYPE,
)
from .phrases import (
    continued_descriptions, coordinated_descriptions, leading_relation,
    post_each_colors, postnoun_attributes, quantity, relation_in,
)
from .edits import FILTER_RELATIONS, read_edit, recolorable
from .references import ReferenceContext, Referent, UnresolvedReference

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
            each_colors = post_each_colors(text[noun.end():], kind)
            if each_colors and noun.end() + each_colors['end'] > separator.start():
                continue
            shared_tail = re.match(r'\s*all\s+(?:(?:not|no|without)\s+)?', text[separator.end():], re.I)
            if shared_tail and leading_relation(text[separator.end()+shared_tail.end():])[0] and (source_groups['descriptions'] or operation and operation.lastgroup in {'add','remove'}):
                continue  # The shared placement belongs to this creation clause.
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


# Cross-request references hold at most this many objects (the scene capacity).
SCENE_LIMIT = 120


def partition_semicolons(text: str) -> str:
    """In "Plant ten trees: three pink; the rest green." the semicolon separates groups like a comma.

    One code point maps to one code point, so highlight offsets stay exact. A semicolon followed by a
    new instruction ("...: red and white; remove them") keeps its meaning.
    """
    out = []
    for sentence in re.finditer(r"[^.!?]+[.!?]*|[.!?]+", text):
        part = sentence.group()
        colon = part.find(":")
        if colon >= 0 and ";" in part[colon:]:
            pieces = part[colon + 1:].split(";")
            rebuilt = pieces[0]
            for piece in pieces[1:]:
                rebuilt += (";" if OPERATION_RE.search(piece) else ",") + piece
            part = part[:colon + 1] + rebuilt
        out.append(part)
    return "".join(out)


def parse(text: str, context: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Ground `text` as world actions.

    `context` lists the object groups the previous command affected, oldest first, as
    the client remembers them ({"type", "count"}). They seed 'it'/'them' so "make it
    blue" can follow "build a castle"; bindings point at them with negative indexes
    (-1 for the first group). The server keeps no state between requests.
    """
    if len(text) > 1400:
        raise ValueError("Please keep commands under 1,400 characters.")
    if not text.strip():
        raise ValueError("Enter a world-building instruction.")
    actions: list[dict[str, Any]] = []
    highlights: list[dict[str, Any]] = []
    warnings: list[str] = []
    references = ReferenceContext()
    for k, group in enumerate(context or []):
        references.groups.append(Referent(group["type"], group["count"], -(k + 1)))
    resolutions, bindings = [], []

    def mark(start: int, end: int, role: str):
        highlight = {"text": text[start:end], "start": start, "end": end, "role": role}
        if highlight not in highlights:
            highlights.append(highlight)

    def mark_reference_span(start, end, groups):
        mark(start, end, 'reference')
        resolutions.append({'text': text[start:end], 'start': start, 'end': end,
                            'objects': [{'type': g.type, 'count': g.count} for g in groups],
                            'earlier': any(g.action_index < 0 for g in groups)})

    def mark_reference(match, offset, groups):
        mark_reference_span(offset + match.start(), offset + match.end(), groups)

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

    def apply_edit(edit, clause, offset):
        """Emit actions for one edit; return where in `clause` it stopped reading."""
        end = edit["end"]
        if edit["verb_span"]:
            mark(offset + edit["verb_span"][0], offset + edit["verb_span"][1], "intent")
        if edit["negated"]:
            warnings.append("Skipped a negated edit; no objects were changed for that clause.")
            return len(clause)
        if not edit["kind"]:
            warnings.append(f"Could not tell how to {edit['verb']} those objects; name a color, bigger/smaller, a direction or a place such as 'behind the lake'.")
            return len(clause)
        landmarks, landmark_groups = [], []
        if edit.get("relation"):
            relation, (relation_start, relation_end) = edit["relation"], edit["relation_span"]
            mark(offset + relation_start, offset + relation_end, "spatial_relation")
            found = list(MENTION_RE.finditer(clause, relation_end))
            landmarks, consumed, landmark_groups = read_landmarks(clause, relation, relation_end, found, 0, offset)
            if not landmarks or relation == "between" and len(landmarks) != 2:
                warnings.append("A move needs a named landmark; use 'move the tree behind the lake' or 'between the house and the lake'.")
                return len(clause)
            end = found[consumed].end()
        elif edit.get("value_span") and edit["value_span"] != edit["verb_span"]:
            mark(offset + edit["value_span"][0], offset + edit["value_span"][1], "color" if edit["kind"] == "recolor" else "change")
        # Resolve every subject before this clause introduces the edited objects as new referents.
        subjects = []
        for target in edit["targets"]:
            span_start, span_end = target["span"]
            if target["pronoun"]:
                try:
                    groups = references.resolve(target["pronoun"])
                except UnresolvedReference as exc:
                    warnings.append(str(exc))
                    continue
                mark_reference_span(offset + span_start, offset + span_end, groups)
                subset = target.get("subset")
                if subset is not None:
                    # "make two of them red": a part of one group; a mixed collection needs an explicit type.
                    if len(groups) != 1 or not 0 < subset <= groups[0].count or target.get("exact") and groups[0].count != subset:
                        warnings.append(f"'{text[offset + span_start:offset + span_end]}' needs one group with at least {subset or 1} object(s); name the objects instead.")
                        continue
                    subjects.append((groups[0].type, subset, [groups[0].action_index], None, None))
                    continue
                subjects += [(g.type, g.count, [g.action_index], None, None) for g in groups]
                continue
            mark(offset + span_start, offset + span_end, "object")
            if "number_span" in target:
                mark(offset + target["number_span"][0], offset + target["number_span"][1], "quantity")
            if "filter_span" in target:
                mark(offset + target["filter_span"][0], offset + target["filter_span"][1], "color")
            if target["count"] is None:
                warnings.append(f"Skipped {target['type']}: specify an unambiguous whole-number quantity.")
                continue
            location = target.get("location")
            if location:
                mark(offset + location["relation_span"][0], offset + location["relation_span"][1], "spatial_relation")
                mark(offset + location["target_span"][0], offset + location["target_span"][1], "landmark")
            subjects.append((target["type"], target["count"], None, target["filter"], location))
        first = True
        for kind, count, sources, color_filter, location in subjects:
            if edit["kind"] == "recolor" and not recolorable(kind):
                warnings.append(f"{kind.capitalize()}s have no color to change; houses, trees and flowers can be repainted.")
                continue
            action = {"action": edit["kind"], "type": kind, "count": count if count == "all" else min(count, SCENE_LIMIT)}
            if edit["kind"] == "recolor":
                action["color"] = edit["color"]
            elif edit["kind"] == "resize":
                action["scale"] = edit["scale"]
            elif edit.get("relation"):
                action.update(relation=edit["relation"], target=landmarks[0])
                if edit["relation"] == "between":
                    action["targets"] = landmarks
            else:
                action.update(direction=edit["direction"], distance=edit["distance"])
            if color_filter:
                action["filter_color"] = color_filter
            if location:
                action.update(filter_relation=location["relation"], filter_target=location["target"])
            binding = {}
            if sources:
                binding["edit_from"] = sources
            if landmark_groups:
                binding["target_from"] = [g.action_index for g in landmark_groups]
            if binding:
                bindings.append({"action_index": len(actions), **binding})
            references.introduce(kind, count if count != "all" else SCENE_LIMIT, len(actions), new_clause=first)
            first = False
            actions.append(action)
        return end

    inherited_intent, inherited_negated = "add", False
    last_edit = None
    # One code point maps to one code point: original UI spans stay exact.
    matched_text = partition_semicolons(text.translate(MATCH_TRANSLATION))
    for offset, clause, continuation in clauses(matched_text):
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
        edit = read_edit(clause, last_edit if continuation else None)
        if edit:
            # "Make the trees purple and the houses red": coordinated edits share one verb.
            while edit:
                end = apply_edit(edit, clause, offset)
                last_edit, clause, offset = edit, clause[end:], offset + end
                edit = read_edit(clause, last_edit) if clause.strip(" .") else None
            if clause.strip(" ."):
                warnings.append(f"Ignored words after the edit: '{clause.strip()}'.")
            inherited_intent = "edit"
            continue
        last_edit = None
        if continuation and not operation and inherited_intent == "edit":
            warnings.append("Could not read that part of the edit; name the object and its new color, size or place.")
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

        # Resolve a shared comma tail before any source objects enter references.
        shared_relation, shared_targets, shared_groups = None, [], []
        shared = re.search(r',\s*all\s+(?:(?:not|no|without)\s+)?',clause,re.I)
        if shared:
            shared_relation, shared_match = leading_relation(clause[shared.end():])
            if shared_relation:
                relation_start = shared.end() + shared_match.start()
                relation_end = shared.end() + shared_match.end()
                found = list(MENTION_RE.finditer(clause,relation_end))
                shared_targets, consumed, shared_groups = read_landmarks(clause,shared_relation,relation_end,found,0,offset)
                mark(offset+relation_start,offset+relation_end,'spatial_relation')
                if (intent != 'add' or NEGATION_RE.search(shared.group()) or relation_in(clause[:shared.start()])[0]
                        or not shared_targets or shared_relation=='between' and len(shared_targets)!=2 or consumed!=len(found)-1):
                    warnings.append('A shared placement needs one unambiguous, positive location and named landmarks; that creation clause was skipped.')
                    continue
                clause = clause[:shared.start()]
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
            each_colors = post_each_colors(clause[entity.end():],kind)
            if each_colors:
                attribute_error = each_colors['error']
                if count is None or number is None or variants is not None or color:
                    attribute_error = attribute_error or 'Of each color needs one explicit count without conflicting source colors; that instruction was skipped.'
                variants = [{'count':count, 'color':c.group().lower(), 'number':number,
                             'color_match':None,'offset':0,'negated':bool(NEGATION_RE.search(prefix))} for c in each_colors['colors']] if not attribute_error else []
                attributes['end'] = each_colors['end']
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
                if (not declared_total or count is None or not continued['first_comma'] or any(
                        d['fraction'][0] is None or not 0 <= d['fraction'][0] <= d['fraction'][1]
                        or count*d['fraction'][0] % d['fraction'][1] for d in fractions)):
                    attribute_error = 'Fraction groups need a declared total giving non-negative whole-object counts and a partition; that instruction was skipped.'
                else:
                    for description in fractions:
                        numerator,denominator = description['fraction']
                        description['count'] = count*numerator // denominator
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
                    attribute_error = attribute_error or 'Partition counts do not match the declared total; that object instruction was skipped.'
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
            if shared_relation:
                relation, targets, target_groups = shared_relation,shared_targets,shared_groups
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
            for each_color in each_colors['colors'] if each_colors else []:
                mark(offset+entity.end()+each_color.start(),offset+entity.end()+each_color.end(),'color')
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
            elif intent == "remove" and relation and (relation not in FILTER_RELATIONS or len(targets) != 1 or target_groups):
                warnings.append("Removal can be filtered by one named landmark: near, left of, right of, behind, in front of or inside it. "
                                "For example 'remove the trees near the lake'.")
            elif intent == 'remove' and (variants is not None or continued['descriptions']):
                warnings.append('Coordinated removal descriptions are not supported; specify an object type and quantity.')
            elif intent == "remove":
                # "Remove the house" names one object; plurals, collectives
                # ("the village") and every/each/all quantifiers mean all.
                singular = (entity.group().lower() in SINGULAR_NOUNS
                            and not re.search(r'\b(?:all|every|each)\b', prefix, re.I))
                amount = min(count, MAX_PER_COMMAND) if number or attributes['has_quantity'] else 1 if singular else 'all'
                action = {"action": "remove", "type": kind, "count": amount}
                if relation:
                    # "Remove the trees near the lake": which trees depends on the scene, so the
                    # scene matches the place; references to earlier groups are left untouched.
                    action.update(filter_relation=relation, filter_target=targets[0])
                else:
                    references.consume(kind, amount)
                actions.append(action)
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
            warnings.append("No supported object or setting found in one clause. Name an object such as a house, tree or lake, or ask for night, rain or snow.")

    for ellipsis in re.finditer(r'\bones\b', text, re.I):
        if not any(h['role'] == 'object' and h['start'] == ellipsis.start() for h in highlights):
            warnings.append('Could not resolve an inherited noun outside an adjacent creation group; use an explicit object noun.')
    # A color the person typed must never vanish silently: if actions were created but a color word
    # was not consumed by any of them and nothing else explained why, say so.
    if actions and not warnings:
        covered = [(h["start"], h["end"]) for h in highlights if h["role"] in {"color", "protected"}]
        for color in COLOR_RE.finditer(text):
            if not any(start <= color.start() and color.end() <= end for start, end in covered) \
                    and not NEGATION_RE.search(text[max(0, color.start() - 24):color.start()]):
                warnings.append(f"The color '{color.group().lower()}' was not used: colors apply to the objects being created, and landmarks are matched by type only.")
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
