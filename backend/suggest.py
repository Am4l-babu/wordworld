"""Typo suggestions: "Did you mean ...?" when a misspelled word costs a command its meaning.

The grounding rules need exact vocabulary. One misspelled word either turns a command into nothing or,
worse, into a partial result that quietly ignores the word ("one bule house" still builds the house, in
no color). For each word close to the vocabulary we try its nearest candidates and keep a correction only
if re-parsing the sentence is measurably better: fewer notices, or actions that now use the word.
Suggestions are never applied automatically; the app shows the corrected sentence and the person decides.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any, Callable

from . import edits, lexicon, parser, phrases
from .lexicon import ALIASES, COLORS, NEGATION_RE, NUMBER_VALUES

# Words the grammar understands, as single tokens. Phrases ("in front of") are matched word by word.
COMMANDS = [
    "add", "build", "create", "place", "put", "plant", "grow", "make", "draw", "remove", "delete", "erase", "destroy",
    "paint", "colour", "color", "recolor", "dye", "move", "shift", "relocate", "slide", "enlarge", "shrink", "resize",
    "bigger", "larger", "smaller", "taller", "shorter", "near", "beside", "behind", "above", "below", "between", "inside",
    "across", "front", "left", "right", "night", "daytime", "rain", "raining", "snow", "snowing", "clear", "reset",
    "every", "both", "half", "quarter", "third", "dozen", "pair", "couple", "several", "remaining", "remainder",
]
# Canonical object nouns first, in the order the lexicon lists them ("house" before "homes"), so ties between
# equally close words go to the word people most likely meant.
VOCABULARY = list(dict.fromkeys([w for words in ALIASES.values() for w in words] + list(COLORS) + COMMANDS + list(NUMBER_VALUES)))


def grammar_words() -> set[str]:
    """Every word spelled out in the grammar's own regex patterns ("show", "whose", "remaining", ...).

    Read from the source rather than listed by hand, so a word the parser understands can never be
    mistaken for a typo, and a verb added to the grammar is automatically suggestible.
    """
    words: set[str] = set()
    for module in (lexicon, phrases, edits, parser):
        for node in ast.walk(ast.parse(Path(module.__file__).read_text(encoding="utf-8"))):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and re.search(r"[\\|]|\(\?", node.value):
                text = re.sub(r"\\[A-Za-z]", " ", node.value)  # drop escapes such as \b and \s before reading words
                words.update(w.lower() for w in re.findall(r"[A-Za-z]{3,}", text))
    return words


GRAMMAR_WORDS = grammar_words()
VOCABULARY += sorted(GRAMMAR_WORDS - set(VOCABULARY))
VOCABULARY_SET = set(VOCABULARY)
RANK = {word: i for i, word in enumerate(VOCABULARY)}
# Words the grammar relies on, or ordinary English that merely resembles vocabulary: never "correct" these.
KEEP = {
    "then", "with", "that", "this", "them", "they", "what", "when", "where", "from", "into", "onto", "over", "also", "just",
    "some", "very", "here", "there", "have", "will", "would", "could", "should", "each", "total", "roofs", "leaves", "petals",
    "painted", "whose", "next", "close", "closer", "around", "along", "their", "about", "these", "those", "than", "much",
    "little", "please", "again", "world", "island", "scene", "sizes", "ones", "other", "same", "small", "large", "tiny",
    "rest", "exactly", "already", "recently", "freshly", "newly", "being", "been", "coloured", "colored", "turn",
    "tall", "short", "wide", "cozy", "lovely", "pretty", "nice", "huge", "giant", "slightly", "more", "less",
    "percent", "such", "like", "most", "many", "never", "only", "were", "does", "done", "went", "gone", "must",
}
# A negation word that is misspelled is a safety problem, not a cosmetic one: "nefer remove them" removes what the person forbade.
NEGATION_WORDS = {"not", "never", "without", "cannot"} & set(re.findall(r"[a-z]{3,}", NEGATION_RE.pattern))  # whole words only, not contraction fragments
# Notices that report a deliberate, correct skip ("Skipped a negated instruction") are not signs of confusion.
DELIBERATE_NOTICES = ("Skipped a negated", "Skipped negated", "Preserved referenced objects")
WORD = re.compile(r"[A-Za-z]+")
MIN_LENGTH = 3
MAX_CHANGES = 4
CANDIDATES_PER_WORD = 3
MAX_PARSES = 24


def distance(a: str, b: str) -> int:
    """Edit distance counting an adjacent swap ("nigth" for "night") as one edit (optimal string alignment)."""
    rows = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1):
        rows[i][0] = i
    for j in range(len(b) + 1):
        rows[0][j] = j
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            cost = a[i - 1] != b[j - 1]
            rows[i][j] = min(rows[i - 1][j] + 1, rows[i][j - 1] + 1, rows[i - 1][j - 1] + cost)
            if i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                rows[i][j] = min(rows[i][j], rows[i - 2][j - 2] + 1)
    return rows[-1][-1]


def allowed_edits(length: int) -> int:
    """Short words tolerate one edit; longer words two."""
    return 1 if length <= 6 else 2


def candidates(word: str) -> list[str]:
    """Vocabulary words within a typo's reach, nearest first. Typos rarely change the first letter, and a
    typo ending in "s" more likely meant a plural, so equally close words that agree on that come first."""
    lower = word.lower()
    if len(lower) < MIN_LENGTH or lower in VOCABULARY_SET or lower in KEEP:
        return []
    limit = allowed_edits(len(lower))
    scored = []
    for candidate in VOCABULARY:
        if candidate[0] != lower[0] or abs(len(candidate) - len(lower)) > limit or len(candidate) < 4 and len(lower) < 4:
            continue
        d = distance(lower, candidate)
        if d <= limit:
            scored.append((d, candidate.endswith("s") != lower.endswith("s"), RANK[candidate], candidate))
    return [c for *_, c in sorted(scored)[:CANDIDATES_PER_WORD]]


def close_match(word: str) -> str | None:
    found = candidates(word)
    return found[0] if found else None


def with_case(original: str, replacement: str) -> str:
    if original.isupper() and len(original) > 1:
        return replacement.upper()
    return replacement.capitalize() if original[:1].isupper() else replacement


def understood(result: dict[str, Any]) -> int:
    """Characters of the sentence the grammar highlighted: "a dozen" counts for more than "a"."""
    return sum(h["end"] - h["start"] for h in result["highlights"])


def confusion(result: dict[str, Any]) -> int:
    """Notices that signal the parser did not understand something; deliberate skips do not count."""
    return sum(1 for w in result["warnings"] if not w.startswith(DELIBERATE_NOTICES))


def progress(new: dict[str, Any], old: dict[str, Any], word: str = "") -> bool:
    """Is `new` a step toward understanding the sentence? Fewer confusing notices, or more of it highlighted.

    Intermediate steps need not produce actions: with two typos, neither fix alone may be enough. Restoring a
    negation word counts whenever it changes what will be done, because the typo made the command do the opposite.
    """
    if word.lower() in NEGATION_WORDS and new["actions"] != old["actions"]:
        return True
    if confusion(new) != confusion(old):
        return confusion(new) < confusion(old)
    return understood(new) > understood(old)


def standing(result: dict[str, Any], edits: int, rank: int) -> tuple[int, int, int, int]:
    """Order competing corrections of the same word: fewest notices, then the closest word (fewest edits, so a
    longer plural is not preferred just because it highlights more text), then most understood, then most canonical."""
    return (-confusion(result), -edits, understood(result), -rank)


def suggest(text: str, parse: Callable[..., dict[str, Any]], context: list[dict[str, Any]] | None = None,
            base: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Return at most one suggestion: {"text", "changes": [{"from", "to", "start", "end"}], "actions", "replaces"}.

    "replaces" is True when the original command already produced actions that the suggestion would change.
    """
    words = [(m, candidates(m.group())) for m in WORD.finditer(text)]
    words = [(m, found) for m, found in words if found]
    if not words or len(words) > 2 * MAX_CHANGES:
        return []
    try:
        original = base or parse(text, context)
    except ValueError:
        return []
    current_text, current, changes, parses = text, original, [], 0
    for match, found in words:
        if len(changes) >= MAX_CHANGES or parses >= MAX_PARSES:
            break
        start = match.start() + sum(len(c["to"]) - (c["end"] - c["start"]) for c in changes)
        best = None
        for replacement in found:
            replacement = with_case(match.group(), replacement)
            attempt = current_text[:start] + replacement + current_text[start + len(match.group()):]
            parses += 1
            try:
                result = parse(attempt, context)
            except ValueError:
                continue
            rank = standing(result, distance(match.group().lower(), replacement.lower()), RANK.get(replacement.lower(), 0))
            if progress(result, current, replacement) and (best is None or rank > best[0]):
                best = (rank, replacement, attempt, result)
        if best:
            _, replacement, current_text, current = best
            changes.append({"from": match.group(), "to": replacement, "start": match.start(), "end": match.end()})
    # The final sentence must produce actions, and must not merely re-state what the original already did.
    if not changes or not current["actions"]:
        return []
    if original["actions"] and current["actions"] == original["actions"] and confusion(current) >= confusion(original):
        return []
    return [{"text": current_text, "changes": changes, "actions": len(current["actions"]), "replaces": bool(original["actions"])}]
