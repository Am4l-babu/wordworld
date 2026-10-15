"""Edits to objects that already exist: recolor, resize and move, read from one clause.

The reader is lexical and deterministic like the rest of the grammar. It only claims a
clause when the edit is unambiguous: "make the houses blue" edits, while "make two blue
houses" still creates objects through the creation grammar.
"""
from __future__ import annotations

import re

from .lexicon import (
    CHANGE_VERBS, COLORS, COLOR_PARTS, MOVE_VERBS, NUMERAL, PAINT_VERBS, RESIZE_VERBS, SINGULAR_NOUNS, WORD_TO_TYPE,
)
from .phrases import leading_relation, number_value

_NOUN = "|".join(sorted(map(re.escape, WORD_TO_TYPE), key=len, reverse=True))
_COLOR = "|".join(COLORS)
_LEAD = r"^\s*(?:(?:please|and|then|now|also|next|so|can\s+you|could\s+you)\s+)*"
_DET = (rf"(?P<det>all\s+(?:of\s+)?(?:the\s+)?|every\s+|each\s+(?:of\s+the\s+)?|both\s+(?:of\s+the\s+)?|(?:the\s+)?(?P<num>{NUMERAL})\s+(?:of\s+the\s+)?"
        rf"|the\s+|that\s+|this\s+|these\s+|those\s+|my\s+)?")
NP_RE = re.compile(rf"\s*(?:(?P<pronoun>it|them)|{_DET}(?:(?P<filter>{_COLOR})\s+)?(?P<noun>{_NOUN}))\b", re.I)
HEAD_RE = re.compile(rf"{_LEAD}(?P<neg>(?:do\s+not|don'?t|never)\s+)?(?P<verb>{PAINT_VERBS}|{MOVE_VERBS}|{RESIZE_VERBS}|{CHANGE_VERBS}|give)\b", re.I)
# "give the cottage a red roof": a color for the part the sprite draws.
PART_COLOR_RE = re.compile(rf"\s*(?:an?\s+)?(?:(?:bright|light|dark|pale)\s+)?(?P<color>{_COLOR})\s+(?:roofs?|leaves|foliage|petals?|colou?r)\b", re.I)
JOIN_RE = re.compile(r"\s*(?:,\s*(?:and\s+)?|\s+and\s+)(?=\s*(?:it|them|all|every|each|the|that|this|these|those|my|\w+\s+of\s+the)\b)", re.I)
COLOR_VALUE_RE = re.compile(rf"\s*(?:(?:to|into|in|with)\s+)?(?:(?:be|become)\s+)?(?:(?:the\s+)?colou?r\s+)?(?:a\s+)?(?:(?:bright|light|dark|pale)\s+)?(?P<color>{_COLOR})\b", re.I)
SIZE_VALUE_RE = re.compile(r"\s*(?:(?:to\s+be|look)\s+)?(?P<amount>much|a\s+lot|way|a\s+(?:bit|little)|slightly|even)?\s*(?P<size>bigger|larger|taller|wider|smaller|tinier|shorter|huge|giant|tiny|big|large|small|little)\b", re.I)
AMOUNT_RE = re.compile(r"\s*(?P<amount>much|a\s+lot|way|a\s+(?:bit|little)|slightly)\b", re.I)
DIRECTION_RE = re.compile(r"\s*(?P<amount>a\s+(?:bit|little)|slightly|far|a\s+lot|way)?\s*(?:(?:over\s+)?(?:to(?:wards?)?\s+the|to)\s+)?(?P<dir>left|right|up|down|forwards?|backwards?|back|north|south|east|west)\b(?!\s+of\b)"
                          r"(?:\s+(?P<after>a\s+(?:bit|little)|slightly|a\s+lot|far))?", re.I)
MOVE_AMOUNT_RE = re.compile(r"\s*(?:(?:a\s+(?:bit|little)|slightly|much)\s+)?", re.I)
DIRECTIONS = {"left": "left", "west": "left", "right": "right", "east": "right", "up": "up", "back": "up", "backward": "up",
              "backwards": "up", "north": "up", "down": "down", "forward": "down", "forwards": "down", "south": "down"}
GROW = {"bigger", "larger", "taller", "wider", "huge", "giant", "big", "large"}
COLLECTIVE = {"village", "town", "forest", "woods", "woodland", "garden"}


def _scale(word: str, amount: str | None) -> float:
    strength = (amount or "").lower()
    step = 0.5 if strength in {"much", "a lot", "way"} else 0.12 if strength in {"a bit", "a little", "slightly"} else 0.25
    return round(1 + step, 2) if word.lower() in GROW or word.lower() == "enlarge" else round(1 / (1 + step), 2)


def _target(match: re.Match, base: int) -> dict:
    span = (base + match.start("pronoun"), base + match.end("pronoun")) if match.group("pronoun") else (base + match.start("noun"), base + match.end("noun"))
    if match.group("pronoun"):
        return {"pronoun": match.group("pronoun").lower(), "span": span, "definite": True}
    noun = match.group("noun").lower()
    det = (match.group("det") or "").lower().strip()
    if match.group("num"):
        count = number_value(match.group("num").lower())
    elif det.startswith("both"):
        count = 2
    elif det.startswith(("all", "every", "each")) or noun not in SINGULAR_NOUNS or noun in COLLECTIVE:
        count = "all"
    else:
        count = 1
    # "two of the houses" names existing objects; "two houses" may describe new ones.
    definite = bool(det) and not (match.group("num") and "of the" not in det and not det.startswith("the"))
    target = {"pronoun": None, "type": WORD_TO_TYPE[noun], "count": count, "span": span, "definite": definite,
              "filter": match.group("filter").lower() if match.group("filter") else None}
    if match.group("num"):
        target["number_span"] = (base + match.start("num"), base + match.end("num"))
    if match.group("filter"):
        target["filter_span"] = (base + match.start("filter"), base + match.end("filter"))
    return target


def _read_targets(clause: str, start: int):
    targets, cursor = [], start
    while True:
        match = NP_RE.match(clause, cursor)
        if not match:
            return targets, cursor
        targets.append(_target(match, 0))
        cursor = match.end()
        join = JOIN_RE.match(clause, cursor)
        if not join or not NP_RE.match(clause, join.end()):
            return targets, cursor
        cursor = join.end()


def read_edit(clause: str, inherited: dict | None = None) -> dict | None:
    """Return the edit described by `clause`, or None when it is not an edit.

    `inherited` is the previous edit in a comma continuation ("paint the house blue,
    the tree pink"), whose verb carries over to a clause that starts with a target.
    """
    head = HEAD_RE.match(clause)
    if head:
        verb = re.sub(r"\s+", " ", head.group("verb").lower())
        start, verb_span, negated = head.end(), (head.start("verb"), head.end("verb")), bool(head.group("neg"))
    elif inherited and NP_RE.match(clause, len(re.match(r"\s*(?:and\s+)?", clause).group())):
        verb, start, verb_span, negated = inherited["verb"], len(re.match(r"\s*(?:and\s+)?", clause).group()), None, False
    else:
        return None
    targets, cursor = _read_targets(clause, start)
    rest = clause[cursor:]
    edit = {"verb": verb, "verb_span": verb_span, "negated": negated, "targets": targets}
    family = ("paint" if re.fullmatch(PAINT_VERBS, verb) else "move" if re.fullmatch(MOVE_VERBS, verb)
              else "resize" if re.fullmatch(RESIZE_VERBS, verb) else "give" if verb == "give" else "change")
    if family == "give":
        color = PART_COLOR_RE.match(rest)
        if not color or not all(t["definite"] for t in targets):
            return None  # "give me two houses" stays a creation request
        edit.update(kind="recolor", color=color.group("color").lower(), value_span=(cursor + color.start("color"), cursor + color.end("color")), end=cursor + color.end())
    elif family in {"paint", "change"} and (color := COLOR_VALUE_RE.match(rest)):
        edit.update(kind="recolor", color=color.group("color").lower(), value_span=(cursor + color.start("color"), cursor + color.end("color")), end=cursor + color.end())
    elif family in {"change", "resize"} and (size := SIZE_VALUE_RE.match(rest)):
        edit.update(kind="resize", scale=_scale(size.group("size"), size.group("amount")), value_span=(cursor + size.start("size"), cursor + size.end("size")), end=cursor + size.end())
    elif family == "resize" and verb in {"enlarge", "shrink"}:
        amount = AMOUNT_RE.match(rest)
        edit.update(kind="resize", scale=_scale(verb, amount.group("amount") if amount else None), value_span=verb_span, end=cursor + (amount.end() if amount else 0))
    elif family == "move" and (direction := DIRECTION_RE.match(rest)):
        amount = re.sub(r"\s+", " ", (direction.group("amount") or direction.group("after") or "").lower())
        edit.update(kind="move", direction=DIRECTIONS[direction.group("dir").lower()],
                    distance="small" if amount in {"a bit", "a little", "slightly"} else "large" if amount in {"far", "a lot", "way"} else "medium",
                    value_span=(cursor + direction.start("dir"), cursor + direction.end("dir")), end=cursor + direction.end())
    elif family == "move" and (relation := leading_relation(rest[(lead := MOVE_AMOUNT_RE.match(rest).end()):]))[0]:
        # "a little closer to the house": the amount softens the wording but the place is the same.
        name, match = relation
        edit.update(kind="move", relation=name, relation_span=(cursor + lead + match.start(), cursor + lead + match.end()), end=cursor + lead + match.end())
    elif family == "change":
        return None  # "make two houses", "make it night", "turn the rain off": not an edit
    else:
        edit.update(kind=None, end=cursor)
    if family == "change" and not all(t["definite"] for t in targets):
        return None  # "make two houses blue" may be a creation; leave it to the creation grammar
    if not targets:
        return None if family == "change" else {**edit, "kind": None}
    return edit


def recolorable(kind: str) -> bool:
    return kind in COLOR_PARTS
