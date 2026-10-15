"""Comparison baseline: read world actions from spaCy's dependency parse.

This module exists to measure the rule-based grounding against a grammar-driven
alternative. It never drives the world: /api/parse applies `backend.parser` actions and
returns these only as a labelled comparison. It shares the lexicon (which words name
objects, colors and numbers) but none of the hand-written phrase patterns; structure
comes only from dependency arcs. Written against the developer's own example sentences,
then frozen before its first run on the labelled sets.
"""
from __future__ import annotations

from typing import Any

from .lexicon import COLORS, MAX_PER_COMMAND, WORD_TO_TYPE
from .phrases import number_value

VERBS = {
    **dict.fromkeys(["add", "build", "create", "place", "put", "plant", "grow", "make", "draw", "generate", "insert"], "add"),
    **dict.fromkeys(["remove", "delete", "erase", "destroy"], "remove"),
    **dict.fromkeys(["paint", "color", "colour", "recolor", "dye"], "recolor"),
    **dict.fromkeys(["move", "shift", "relocate"], "move"),
    **dict.fromkeys(["enlarge", "shrink"], "resize"),
}
DEFAULT_COUNTS = {"village": 4, "villages": 4, "town": 4, "towns": 4, "forest": 6, "forests": 6, "woods": 6, "garden": 5, "gardens": 5}
TIME = {"night": "night", "nighttime": "night", "midnight": "night", "day": "day", "daytime": "day", "daylight": "day", "morning": "day"}
WEATHER = {"rain": "rain", "rainy": "rain", "raining": "rain", "storm": "rain", "snow": "snow", "snowy": "snow", "snowing": "snow"}
NEAR = {"near", "beside", "by", "around", "alongside", "next", "close"}
GROW = {"bigger", "larger", "huge", "big", "large"}


def _negated(token) -> bool:
    return any(child.dep_ == "neg" or child.lower_ in {"never", "no"} for child in token.children)


def _conjuncts(token):
    yield token
    for child in token.children:
        if child.dep_ == "conj":
            yield from _conjuncts(child)


def _object_type(token):
    return WORD_TO_TYPE.get(token.lower_)


def _count(noun, intent):
    """Count from the noun's own dependents: nummod, determiner, or a 'pair of' head."""
    for child in noun.children:
        if child.dep_ == "nummod":
            try:
                return number_value(child.lower_)
            except KeyError:
                return None
        if child.lower_ in {"few", "several"}:
            return 3 if child.lower_ == "few" else 4
        if child.dep_ in {"det", "predet"} and child.lower_ in {"all", "every", "each"}:
            return "all"
    if intent != "add":  # removing or editing "the houses" means all of them
        return 1 if noun.tag_ in {"NN", "NNP"} and noun.lower_ not in DEFAULT_COUNTS else "all"
    return DEFAULT_COUNTS.get(noun.lower_, 1)


def _measure_word(token):
    """'a pair of trees', 'a dozen flowers': return (object noun, multiplier) or None."""
    unit = {"pair": 2, "couple": 2, "dozen": 12}.get(token.lemma_.lower())
    if not unit:
        return None
    for prep in token.children:
        if prep.dep_ == "prep" and prep.lower_ == "of":
            for pobj in prep.children:
                if pobj.dep_ == "pobj" and _object_type(pobj):
                    numbers = [c for c in token.children if c.dep_ == "nummod"]
                    multiplier = number_value(numbers[0].lower_) if numbers else 1
                    return pobj, unit * (multiplier or 1)
    return None


def _color(noun):
    return next((c.lower_ for c in noun.children if c.dep_ in {"amod", "compound", "nmod"} and c.lower_ in COLORS), None)


def _pobj(prep):
    return next((c for c in prep.children if c.dep_ == "pobj"), None)


def _of_object(token):
    for prep in token.children:
        if prep.dep_ == "prep" and prep.lower_ == "of":
            return _pobj(prep)
    return None


def _relation(heads):
    """Find a spatial prepositional phrase attached to the verb or the object noun."""
    for head in heads:
        for child in head.children:
            word = child.lower_
            if child.dep_ == "advmod" and word in {"next", "close"}:
                child = next((c for c in child.children if c.dep_ == "prep" and c.lower_ == "to"), None)
                if child is None:
                    continue
                word = "near"
            elif child.dep_ != "prep":
                continue
            pobj = _pobj(child)
            if pobj is None:
                continue
            if word == "between":
                landmarks = [t for t in _conjuncts(pobj) if _object_type(t)]
                types = [_object_type(t) for t in landmarks]
                if len(types) == 1:
                    count = _count(landmarks[0], "add")
                    types = types * 2 if count == 2 or landmarks[0].tag_ == "NNS" else types
                if len(types) == 2:
                    return "between", types
                continue
            relation, landmark = None, pobj
            if word in NEAR:
                relation = "near"
            elif word in {"behind", "above"}:
                relation = "above"
            elif word in {"below", "under", "beneath"}:
                relation = "below"
            elif word == "in" and pobj.lower_ == "front":
                relation, landmark = "below", _of_object(pobj)
            elif word == "at" and pobj.lower_ == "back":
                relation, landmark = "above", _of_object(pobj)
            elif word in {"to", "on"} and pobj.lower_ in {"left", "right"}:
                relation, landmark = pobj.lower_, _of_object(pobj)
            elif word in {"across", "over", "spanning"}:
                relation = "across"
            elif word in {"in", "inside", "into"}:
                relation = "inside"
            if relation and landmark is not None and _object_type(landmark):
                return relation, [_object_type(landmark)]
    return None, []


def _objects(verb):
    """Direct objects of the verb (and of a 'make X bigger' complement), with coordination."""
    heads = [c for c in verb.children if c.dep_ in {"dobj", "attr", "oprd", "nsubjpass"}]
    for comp in verb.children:
        if comp.dep_ in {"ccomp", "xcomp"}:
            heads += [c for c in comp.children if c.dep_ in {"nsubj", "dobj"}]
    for head in heads:
        for token in _conjuncts(head):
            measured = _measure_word(token)
            if measured:
                yield measured[0], measured[1]
            elif _object_type(token):
                yield token, None


def _verb_value(verb):
    """A color or size that predicates over the object: 'paint the house blue', 'make it bigger'."""
    for child in verb.subtree:
        if child.head.i == verb.i or child.head.dep_ in {"ccomp", "xcomp", "prep"}:
            if child.lower_ in COLORS and child.dep_ not in {"amod", "compound"}:
                return "color", child.lower_
            if child.tag_ == "JJR" or child.lower_ in GROW | {"smaller", "tinier"}:
                return "size", 1.25 if child.lower_ in GROW else 0.8
    return None, None


def extract(doc) -> list[dict[str, Any]]:
    """Return actions in the same schema as backend.parser, read from dependencies only."""
    actions: list[dict[str, Any]] = []
    verbs = [t for t in doc if t.lower_ in VERBS and (t.dep_ in {"ROOT", "conj", "xcomp", "advcl", "ccomp"} or t.pos_ == "VERB")]
    claimed = set()
    for token in doc:
        if token.lower_ in {"clear", "reset"} and token.dep_ in {"ROOT", "conj"} and any(c.lower_ in {"world", "everything", "map"} for c in token.children):
            actions.append({"action": "reset"})
        if token.lower_ in TIME and not _negated(token.head) and not _negated(token):
            actions.append({"action": "setting", "key": "time", "value": TIME[token.lower_]})
        elif token.lower_ in WEATHER:
            negated = _negated(token) or _negated(token.head) or token.head.lower_ in {"without", "no", "stop"}
            actions.append({"action": "setting", "key": "weather", "value": "clear" if negated else WEATHER[token.lower_]})
        if token not in verbs:
            continue
        intent = VERBS[token.lower_]
        if _negated(token):
            continue
        value_kind, value = _verb_value(token)
        if intent == "add" and token.lower_ == "make" and value_kind:
            intent = "recolor" if value_kind == "color" else "resize"
        for noun, measured in _objects(token):
            if noun.i in claimed or _negated(noun) or noun.lower_ in {"it", "them"}:
                continue
            claimed.add(noun.i)
            kind = _object_type(noun)
            count = measured or _count(noun, intent)
            if count is None:
                continue
            if intent == "remove":
                actions.append({"action": "remove", "type": kind, "count": count if count == "all" else min(count, MAX_PER_COMMAND)})
            elif intent == "add":
                action = {"action": "add", "type": kind, "count": min(count, MAX_PER_COMMAND) if count != "all" else 1, "color": _color(noun)}
                relation, targets = _relation([noun, token])
                if relation:
                    action.update(relation=relation, target=targets[0])
                    if relation == "between":
                        action["targets"] = targets
                actions.append(action)
            elif intent == "recolor" and value_kind == "color":
                actions.append({"action": "recolor", "type": kind, "count": count, "color": value})
            elif intent == "resize":
                scale = value if value_kind == "size" else 1.25 if token.lower_ == "enlarge" else 0.8
                actions.append({"action": "resize", "type": kind, "count": count, "scale": scale})
            elif intent == "move":
                relation, targets = _relation([noun, token])
                if relation:
                    action = {"action": "move", "type": kind, "count": count, "relation": relation, "target": targets[0]}
                    if relation == "between":
                        action["targets"] = targets
                    actions.append(action)
    # One setting of each kind, in order, as the rule parser emits.
    seen, unique = set(), []
    for action in actions:
        key = (action["action"], action.get("key"))
        if action["action"] == "setting" and key in seen:
            continue
        seen.add(key)
        unique.append(action)
    return unique[:20]


def extract_text(nlp, text: str) -> list[dict[str, Any]] | None:
    """Run the baseline when the full English model (with a dependency parser) is loaded."""
    if nlp is None or "parser" not in nlp.pipe_names:
        return None
    return extract(nlp(text))
