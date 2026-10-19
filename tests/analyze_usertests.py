r"""Analyse test logs that people downloaded from the app (Share & save -> Test log).

Usage:  .venv\Scripts\python.exe -m tests.analyze_usertests [FOLDER] [--report PATH] [--csv PATH]

FOLDER defaults to evaluation/usertests/ and is read for *.json files. Each file is one person's download. The
analysis reports how often commands worked, which unfamiliar words appear in the ones that did not, how
often "Did you mean" helped, and which logged commands the *current* parser answers differently (drift).

The optional CSV lists commands worth labelling (failed, flagged, or drifted). It leaves the expected-actions column
empty on purpose: gold answers must be written by a person, then frozen into a new evaluation set before any tuning.

Logs hold exactly what testers typed. Get their consent, and keep identifying files out of version control
(evaluation/usertests/*.json is git-ignored).
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path

from backend import parser
from backend.suggest import VOCABULARY_SET

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DIR = ROOT / "evaluation" / "usertests"
# Function words that carry no vocabulary meaning; they would drown out the real gaps.
COMMON = set("""the and for with that this then than them they their what when where which while will would could should have has had was were are been being
into onto from over under about after before also just some very here there again please can you your our out off all any each every both more most less much many
not but its it's it is a an of to in on at by or as be if so do does did me my we us i""".split())
OUTCOMES = ("applied", "nothing", "rejected", "preview")


def load(folder: Path):
    """Return (entries, problems). Entries are de-duplicated by id across files and tagged with their source file."""
    entries, problems, seen = [], [], set()
    for path in sorted(folder.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            problems.append(f"{path.name}: unreadable ({exc.__class__.__name__})")
            continue
        if not isinstance(data, dict) or data.get("app") != "wordworld-testlog" or data.get("schema") != 1 or not isinstance(data.get("entries"), list):
            problems.append(f"{path.name}: not a WordWorld test log (schema 1)")
            continue
        for entry in data["entries"]:
            if not isinstance(entry, dict) or not isinstance(entry.get("text"), str) or entry.get("outcome") not in OUTCOMES or entry.get("id") in seen:
                continue
            seen.add(entry.get("id"))
            entries.append({**entry, "source": path.name})
    return entries, problems


def unknown_words(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z]{3,}", text.lower()) if w not in VOCABULARY_SET and w not in COMMON]


def current_actions(entry):
    try:
        return parser.parse(entry["text"], [{"type": g["type"], "count": g["count"]} for g in entry.get("context") or [] if g.get("count")])["actions"]
    except ValueError:
        return None


def analyse(entries):
    total = len(entries)
    outcome = Counter(e["outcome"] for e in entries)
    flagged = [e for e in entries if e.get("flagged")]
    failed = [e for e in entries if e["outcome"] in {"nothing", "rejected"}]
    shown = [e for e in entries if e.get("suggestion")]
    drift, rows = [], []
    for e in entries:
        now = current_actions(e)
        changed = now is not None and e["outcome"] != "preview" and now != (e.get("actions") or [])
        if changed:
            drift.append(e)
        e["_now"] = now
        e["_drift"] = changed
    gaps = Counter(w for e in failed + flagged for w in set(unknown_words(e["text"])))
    background = Counter(w for e in entries if e["outcome"] == "applied" and not e.get("flagged") for w in set(unknown_words(e["text"])))
    return {
        "testers": len({e["source"] for e in entries}), "commands": total, "outcomes": dict(outcome),
        "works": round(outcome["applied"] / total, 4) if total else None,
        "flagged": len(flagged), "flagged_but_applied": sum(1 for e in flagged if e["outcome"] == "applied"),
        "suggestions_shown": len(shown), "suggestions_accepted": sum(1 for e in shown if e.get("suggestionAccepted")),
        "phone": sum(1 for e in entries if e.get("device") == "phone"),
        "drift": len(drift), "gaps": gaps.most_common(25), "background": background,
    }


def markdown(stats, entries, problems):
    n = stats["commands"]
    pct = lambda k: f"{k} ({k / n:.0%})" if n else "0"
    lines = ["# User test results", "",
             f"{stats['testers']} tester file(s), {n} commands ({stats['phone']} on phones).", ""]
    if problems:
        lines += ["**Skipped files:** " + "; ".join(problems), ""]
    if not n:
        return "\n".join(lines + ["No commands to analyse."]) + "\n"
    o = stats["outcomes"]
    lines += ["| Outcome | Commands |", "|---|---|",
              f"| Changed the world | {pct(o.get('applied', 0))} |", f"| Understood as nothing | {pct(o.get('nothing', 0))} |",
              f"| Refused by the API | {pct(o.get('rejected', 0))} |", f"| Answered by the offline preview | {pct(o.get('preview', 0))} |", "",
              f"- **Marked “not what I meant”:** {stats['flagged']}, of which {stats['flagged_but_applied']} had changed the world: the dangerous kind, a wrong result with no warning.",
              f"- **“Did you mean” shown / accepted:** {stats['suggestions_shown']} / {stats['suggestions_accepted']}.",
              f"- **Drift:** {stats['drift']} logged command(s) get different actions from the current parser than when they were typed.", ""]
    if stats["gaps"]:
        lines += ["## Words the grammar does not know, in commands that failed or were flagged", "",
                  "Frequent entries are vocabulary gaps (a new object, color or verb) or typos the suggester missed. “Also in working commands” separates real gaps from ordinary English.", "",
                  "| Word | Failed/flagged commands | Also in working commands |", "|---|---|---|",
                  *[f"| {w} | {c} | {stats['background'].get(w, 0)} |" for w, c in stats["gaps"]], ""]
    notes = [e for e in entries if e.get("note")]
    if notes:
        lines += ["## What testers said they expected", "", *[f"- “{e['text']}” → *{e['note']}*" for e in notes[:40]], ""]
    silent = [e for e in entries if e.get("flagged") and e["outcome"] == "applied"]
    if silent:
        lines += ["## Flagged although the world changed (check these first)", "", *[f"- “{e['text']}”" + (f" → *{e['note']}*" if e.get("note") else "") for e in silent[:40]], ""]
    return "\n".join(lines) + "\n"


def write_csv(path: Path, entries):
    """Candidates for hand labelling. expected_actions stays empty: a person writes it, then it is frozen before tuning."""
    fields = ["source", "id", "text", "context", "logged_outcome", "logged_actions", "current_actions", "warnings", "note", "expected_actions", "label_notes"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for e in entries:
            if e["outcome"] == "applied" and not e.get("flagged") and not e["_drift"]:
                continue
            writer.writerow({"source": e["source"], "id": e.get("id"), "text": e["text"], "context": json.dumps(e.get("context") or []),
                             "logged_outcome": e["outcome"], "logged_actions": json.dumps(e.get("actions") or []),
                             "current_actions": json.dumps(e["_now"]) if e["_now"] is not None else "", "warnings": " | ".join(e.get("warnings") or []),
                             "note": e.get("note", ""), "expected_actions": "", "label_notes": ""})


def main():
    args = argparse.ArgumentParser()
    args.add_argument("folder", nargs="?", type=Path, default=DEFAULT_DIR)
    args.add_argument("--report", type=Path)
    args.add_argument("--csv", type=Path)
    options = args.parse_args()
    if not options.folder.is_dir():
        raise SystemExit(f"{options.folder} is not a folder. Create it and put the downloaded test logs inside.")
    entries, problems = load(options.folder)
    stats = analyse(entries)
    text = markdown(stats, entries, problems)
    print(text)
    if options.report:
        options.report.write_text(text, encoding="utf-8", newline="\n")
    if options.csv:
        write_csv(options.csv, entries)
        print(f"Candidates written to {options.csv} (expected_actions is blank: label by hand, then freeze before tuning).")


if __name__ == "__main__":
    main()
