r"""Measure typo robustness: how often "Did you mean ...?" restores a command's exact gold actions.

Usage:  .venv\Scripts\python.exe -m tests.evaluate_typos [--seed N] [--json PATH] [--report PATH]

Every labelled command whose gold actions are non-empty gets ONE synthetic typo in a vocabulary word the
grounding rules need (a deletion, duplicated letter, adjacent swap, or substituted letter), generated from a
fixed seed. Outcomes per corrupted command:

  harmless   the corrupted command still parses to the gold actions
  recovered  it did not, but the first suggestion parses to the gold actions
  wrong fix  a suggestion was offered but does not parse to the gold actions
  missed     no suggestion at all (the command parsed to nothing, or to something else, and nothing was offered)

"Silent error" counts corrupted commands that parse to actions different from gold with no suggestion: the
person gets a wrong world instead of a hint. Synthetic noise is not human typing; keyboard-adjacent
substitutions are approximated with a QWERTY neighbour map. The suggester was tuned on seed 1; the reported
numbers use a seed nobody has inspected. Seed 2 was viewed once while writing the first report (and that exposed a tie-break bias), so it is reported but no longer counts as untouched.
"""
from __future__ import annotations

import argparse
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

from backend import parser
from backend.suggest import VOCABULARY_SET, suggest

ROOT = Path(__file__).resolve().parents[1]
TUNING_SEED, REVIEWED_SEED, REPORT_SEED = 1, 2, 3
KINDS = ("deletion", "duplication", "swap", "substitution")
NEIGHBOURS = {
    "q": "wa", "w": "qes", "e": "wrd", "r": "etf", "t": "ryg", "y": "tuh", "u": "yij", "i": "uok", "o": "ipl", "p": "ol",
    "a": "qsz", "s": "awdx", "d": "sefc", "f": "drgv", "g": "fthb", "h": "gyjn", "j": "huk", "k": "jil", "l": "kop",
    "z": "asx", "x": "zsdc", "c": "xdfv", "v": "cfgb", "b": "vghn", "n": "bhjm", "m": "njk",
}


def labelled_commands():
    sets = [("development", ROOT / "tests/commands.json", "actions")]
    sets.append(("heldout", ROOT / "tests/heldout_commands.json", "expected_actions"))
    sets += [(f"fresh_v{n}", ROOT / f"tests/fresh_commands_v{n}.json", "expected_actions") for n in range(2, 13)]
    for name, path, key in sets:
        data = json.loads(path.read_text(encoding="utf-8"))
        for i, case in enumerate(data if isinstance(data, list) else data["cases"]):
            gold = case[key]
            if gold:
                yield name, case.get("id") or f"D{i + 1:02d}", case["text"], gold, case.get("context")


def corrupt(text: str, rng: random.Random):
    """One typo in a vocabulary word of at least four letters; returns (text, kind, original, typo) or None."""
    words = [m for m in __import__("re").finditer(r"[A-Za-z]+", text) if m.group().lower() in VOCABULARY_SET and len(m.group()) >= 4]
    if not words:
        return None
    match = rng.choice(words)
    word, kind = match.group(), rng.choice(KINDS)
    i = rng.randrange(1, len(word) - 1) if len(word) > 2 else 0  # keep the first letter, as real typos mostly do
    if kind == "deletion":
        typo = word[:i] + word[i + 1:]
    elif kind == "duplication":
        typo = word[:i] + word[i] + word[i:]
    elif kind == "swap":
        typo = word[:i] + word[i + 1] + word[i] + word[i + 2:] if i + 1 < len(word) else word
    else:
        options = NEIGHBOURS.get(word[i].lower(), "e")
        typo = word[:i] + rng.choice(options) + word[i + 1:]
    if typo.lower() == word.lower() or typo.lower() in VOCABULARY_SET:
        return None  # a no-op, or another real word: not a typo we can be expected to notice
    return text[:match.start()] + typo + text[match.end():], kind, word, typo


def run(seed: int):
    rng = random.Random(seed)
    rows = []
    for name, ident, text, gold, context in labelled_commands():
        # Only commands the rules already get right are fair material: otherwise the typo is not what fails.
        if parser.parse(text, context)["actions"] != gold:
            continue
        noisy = corrupt(text, rng)
        if noisy is None:
            continue
        corrupted, kind, original, typo = noisy
        try:
            actions = parser.parse(corrupted, context)["actions"]
        except ValueError:
            continue
        suggestions = suggest(corrupted, parser.parse, context)
        if actions == gold:
            outcome = "harmless"
        elif suggestions and parser.parse(suggestions[0]["text"], context)["actions"] == gold:
            outcome = "recovered"
        elif suggestions:
            outcome = "wrong fix"
        else:
            outcome = "missed"
        rows.append({"set": name, "id": ident, "original": text, "corrupted": corrupted, "kind": kind, "word": original, "typo": typo,
                     "outcome": outcome, "silent_error": bool(actions) and actions != gold and not suggestions,
                     # A suggestion for a typo the rules already tolerated is only a false alarm if it would change the actions.
                     "false_alarm": outcome == "harmless" and bool(suggestions) and parser.parse(suggestions[0]["text"], context)["actions"] != gold,
                     "tidying": outcome == "harmless" and bool(suggestions) and parser.parse(suggestions[0]["text"], context)["actions"] == gold,
                     "suggestion": suggestions[0]["text"] if suggestions else None})
    return rows


def clean_false_alarms():
    """Suggestions made for labelled commands that were already parsed correctly: there should be none."""
    total, alarms = 0, []
    for _name, _ident, text, gold, context in labelled_commands():
        result = parser.parse(text, context)
        if result["actions"] != gold:
            continue
        total += 1
        suggestions = suggest(text, parser.parse, context, base=result)
        if suggestions:
            alarms.append({"text": text, "suggestion": suggestions[0]["text"]})
    return {"checked": total, "false_alarms": len(alarms), "examples": alarms[:12]}


def summarise(rows):
    counts = Counter(r["outcome"] for r in rows)
    needing_help = [r for r in rows if r["outcome"] != "harmless"]
    by_kind = defaultdict(Counter)
    for r in rows:
        by_kind[r["kind"]][r["outcome"]] += 1
    return {
        "corrupted": len(rows), "outcomes": dict(counts),
        "needing_help": len(needing_help),
        "recovery_rate": round(counts["recovered"] / len(needing_help), 4) if needing_help else None,
        "wrong_fix_rate": round(counts["wrong fix"] / len(needing_help), 4) if needing_help else None,
        "silent_errors": sum(r["silent_error"] for r in rows),
        "harmless_false_alarms": sum(r["false_alarm"] for r in rows),
        "harmless_tidying": sum(r["tidying"] for r in rows),
        "by_kind": {k: dict(v) for k, v in sorted(by_kind.items())},
    }


def write_report(path: Path, seeds, rows, clean):
    """`seeds` maps a seed number to its summary; `rows` are the untouched seed's per-command results."""
    def row(label, s):
        o = s["outcomes"]
        return (f"| {label} | {s['corrupted']} | {o.get('harmless', 0)} | {o.get('recovered', 0)} | {o.get('wrong fix', 0)} | {o.get('missed', 0)} | "
                f"{s['recovery_rate']:.0%} | {s['wrong_fix_rate']:.1%} | {s['silent_errors']} |")
    final = seeds[REPORT_SEED]
    lines = [
        "# Typo robustness and the “Did you mean…?” suggester", "",
        "The grounding rules need exact vocabulary, so one misspelled word turns a command into nothing or, worse, into a partial result that quietly "
        "ignores the word (`one bule house` still builds the house, in no color). The suggester (`backend/suggest.py`) tries the nearest vocabulary "
        "words for each unfamiliar word (edit distance, adjacent swaps count as one edit) and keeps a correction only if re-parsing the sentence is "
        "**measurably better**: fewer notices, or more of the sentence understood. The final sentence must produce actions. It never applies a correction "
        "itself: the app shows it and the person decides. The vocabulary is read from the grammar's own regex patterns, so a word the parser understands "
        "(`show`, `whose`, `remaining`) can never be mistaken for a typo.", "",
        "## Method", "",
        "Every labelled command (650 across the development, held-out and twelve fresh sets) that the rules already get exactly right is "
        "corrupted with **one** synthetic typo in a vocabulary word of at least four letters: a deletion, a duplicated letter, an adjacent swap, "
        "or a substitution with a QWERTY neighbour. The first letter is kept, as in most real typing errors. Commands with no gold actions are skipped.", "",
        "- **harmless**: the corrupted command still parses to the gold actions",
        "- **recovered**: it did not, but the first suggestion parses to the gold actions",
        "- **wrong fix**: a suggestion was offered but parses to something else",
        "- **missed**: nothing was offered",
        "- **silent error**: the corrupted command parses to *different* actions and no suggestion is made, so the person gets a wrong world without a hint", "",
        f"**Seeds.** The suggester was developed against seed {TUNING_SEED}. Seed {REVIEWED_SEED} was viewed once while writing the first draft of this report; "
        f"that exposed a real tie-break bias (a longer plural won because it highlights more text), which was fixed on principle, so seed {REVIEWED_SEED} no longer counts as untouched. "
        f"The headline numbers use **seed {REPORT_SEED}**, whose results nobody inspected before this report was generated.", "",
        "| Seed | Corrupted | Harmless | Recovered | Wrong fix | Missed | Recovery of the rest | Wrong-fix rate | Silent errors |", "|---|---|---|---|---|---|---|---|---|",
        row(f"{TUNING_SEED} (tuning)", seeds[TUNING_SEED]), row(f"{REVIEWED_SEED} (reviewed)", seeds[REVIEWED_SEED]), row(f"**{REPORT_SEED} (untouched)**", final), "",
        "## False alarms", "",
        f"- **Already-correct commands:** the suggester was run on all {clean['checked']} labelled commands the rules parse exactly right: **{clean['false_alarms']} suggestions**.",
        f"- **Typos the rules already tolerated** (seed {REPORT_SEED}): {final['harmless_false_alarms']} suggestions that would change the actions; "
        f"{final['harmless_tidying']} that keep exactly the same actions and only tidy the spelling (and drop a notice).", "",
        f"## By typo kind (seed {REPORT_SEED})", "", "| Kind | Harmless | Recovered | Wrong fix | Missed |", "|---|---|---|---|---|",
        *[f"| {k} | {v.get('harmless', 0)} | {v.get('recovered', 0)} | {v.get('wrong fix', 0)} | {v.get('missed', 0)} |" for k, v in final["by_kind"].items()], "",
        f"## What still goes wrong (seed {REPORT_SEED})", "",
    ]
    for outcome, title in (("wrong fix", "Wrong fixes"), ("missed", "Missed")):
        picked = [r for r in rows if r["outcome"] == outcome][:12]
        lines += [f"### {title}", ""]
        lines += [f"- “{r['corrupted']}” ({r['kind']}: {r['typo']} for {r['word']})" + (f" → suggested “{r['suggestion']}”" if r['suggestion'] else "") for r in picked] or ["- none"]
        lines.append("")
    silent = [r for r in rows if r["silent_error"]][:12]
    lines += ["### Silent errors (the typo changed the meaning, and nothing was suggested)", "",
              *([f"- “{r['corrupted']}” ({r['kind']}: {r['typo']} for {r['word']})" for r in silent] or ["- none"]), "",
              "## Limits", "",
              "Synthetic noise is not human typing: real errors include phonetic spellings, missing spaces and autocorrect substitutions that this does not model. "
              "A word that is valid English but not in the vocabulary (`horse` for `house`) can be offered as a correction; that is why a suggestion is only ever shown, never applied. "
              "Two equally close words cannot be told apart without more context (`towes` is one edit from both `towers` and `towns`). "
              "A real English word that is also a one-letter-off typo (`there` for `three`) is left alone on purpose. "
              "Recovery is measured against the gold actions, not against what a person meant.", ""]
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def main():
    args = argparse.ArgumentParser()
    args.add_argument("--json", type=Path)
    args.add_argument("--report", type=Path)
    options = args.parse_args()
    runs = {seed: run(seed) for seed in (TUNING_SEED, REVIEWED_SEED, REPORT_SEED)}
    seeds = {seed: summarise(rows) for seed, rows in runs.items()}
    clean = clean_false_alarms()
    for seed, s in seeds.items():
        o = s["outcomes"]
        label = {TUNING_SEED: "tuning", REVIEWED_SEED: "reviewed", REPORT_SEED: "untouched"}[seed]
        print(f"seed {seed} ({label:9}) corrupted={s['corrupted']} harmless={o.get('harmless', 0)} recovered={o.get('recovered', 0)} wrong={o.get('wrong fix', 0)} "
              f"missed={o.get('missed', 0)} | recovery of rest {s['recovery_rate']:.0%} wrong-fix {s['wrong_fix_rate']:.1%} silent errors {s['silent_errors']} "
              f"| harmless: meaning-changing {s['harmless_false_alarms']}, tidying-only {s['harmless_tidying']}")
    print(f"clean commands: {clean['false_alarms']} false suggestion(s) in {clean['checked']}")
    if options.json:
        options.json.write_text(json.dumps({"seeds": {str(k): v for k, v in seeds.items()}, "clean": clean, "rows": runs[REPORT_SEED]}, indent=2, ensure_ascii=False) + "\n",
                                encoding="utf-8", newline="\n")
    if options.report:
        write_report(options.report, seeds, runs[REPORT_SEED], clean)


if __name__ == "__main__":
    main()
