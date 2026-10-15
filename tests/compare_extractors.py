r"""Compare the rule-based grounding with the dependency-parse baseline on every labelled set.

Usage:  .venv\Scripts\python.exe -m tests.compare_extractors          (write results and report)
        .venv\Scripts\python.exe -m tests.compare_extractors --check  (fail if the saved summary is stale)

Both extractors see the same 550 commands and are scored with the same field definitions
as tests/evaluate_heldout.py. The rule parser was developed with these sets after each
first run, so its retest scores are optimistic; its recorded first-run scores are listed
beside them. The baseline was written against separate example sentences and frozen
(see BASELINE_SHA256) before it was run on any labelled set.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "evaluation/results/extractor_comparison.json"
REPORT = ROOT / "evaluation/reports/extractor_comparison_report.md"
SUMMARY = ROOT / "backend/extractor_scores.json"
BASELINE_SHA256 = "a3fa82150bd5cfac2fd41b0f84d7f25ab733867942376e6d0082c428e9eb529c"
FIELDS = ["exact_match", "intent", "entity_count_color", "spatial"]


def labelled_sets():
    yield "development", "Development regressions (tests/commands.json)", None, [
        {"id": f"D{i + 1:02d}", "text": c["text"], "expected": c["actions"]} for i, c in enumerate(json.loads((ROOT / "tests/commands.json").read_text(encoding="utf-8")))]
    for name, path, first_run in [("heldout", "tests/heldout_commands.json", "evaluation/results/heldout_results.json")] + [
            (f"fresh_v{n}", f"tests/fresh_commands_v{n}.json", f"evaluation/results/fresh_results_v{n}.json") for n in range(2, 12)]:
        data = json.loads((ROOT / path).read_text(encoding="utf-8"))
        cases = [{"id": c["id"], "text": c["text"], "expected": c["expected_actions"], "context": c.get("context")} for c in data["cases"]]
        recorded = json.loads((ROOT / first_run).read_text(encoding="utf-8"))["metrics"]["exact_match"]
        yield name, f"{data['name']} ({path})", recorded, cases


def score(predicted, expected):
    objects = lambda acts: [(a.get("action"), a.get("type"), a.get("count"), a.get("color")) for a in acts if a.get("type")]
    spatial = lambda acts: [(a.get("type"), a.get("relation"), a.get("target"), a.get("targets")) for a in acts if a.get("type")]
    return {
        "exact_match": predicted == expected,
        "intent": [a.get("action") for a in predicted] == [a["action"] for a in expected],
        "entity_count_color": objects(predicted) == objects(expected),
        "spatial": spatial(predicted) == spatial(expected) if any(a.get("relation") for a in expected) else None,
    }


def metrics(rows, key):
    out = {}
    for field in FIELDS:
        values = [r[key][field] for r in rows if r[key][field] is not None]
        out[field] = {"correct": sum(values), "total": len(values), "accuracy": round(sum(values) / len(values), 4) if values else None}
    return out


def run():
    from backend.parser import NLP, parse
    from backend.dependency_baseline import extract
    baseline_sha = hashlib.sha256((ROOT / "backend/dependency_baseline.py").read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    if baseline_sha != BASELINE_SHA256:
        raise SystemExit("backend/dependency_baseline.py changed after it was frozen; version the comparison instead of re-tuning it.")
    if NLP is None or "parser" not in NLP.pipe_names:
        raise SystemExit("The comparison needs the full en_core_web_sm model (dependency parser).")
    sets, everything = [], []
    for name, title, first_run, cases in labelled_sets():
        rows = []
        for case in cases:
            # Rules get the client context a case carries; the baseline has no notion of it.
            rules = parse(case["text"], case.get("context"))["actions"]
            baseline = extract(NLP(case["text"]))
            rows.append({**case, "rules": rules, "baseline": baseline,
                         "rules_score": score(rules, case["expected"]), "baseline_score": score(baseline, case["expected"]),
                         "agree": rules == baseline})
        everything += rows
        sets.append({"name": name, "title": title, "commands": len(rows), "rules": metrics(rows, "rules_score"),
                     "baseline": metrics(rows, "baseline_score"), "agreement": round(sum(r["agree"] for r in rows) / len(rows), 4),
                     "rules_first_run_exact": first_run, "cases": rows})
    summary = {
        "commands": len(everything),
        "rules": metrics(everything, "rules_score"),
        "baseline": metrics(everything, "baseline_score"),
        "agreement": round(sum(r["agree"] for r in everything) / len(everything), 4),
        "rules_first_run_exact": {
            "correct": sum(s["rules_first_run_exact"]["correct"] for s in sets if s["rules_first_run_exact"]),
            "total": sum(s["rules_first_run_exact"]["total"] for s in sets if s["rules_first_run_exact"]),
            "sets": sum(1 for s in sets if s["rules_first_run_exact"]),
        },
        "baseline_sha256": baseline_sha,
        "note": "Rule scores are retests on sets used during development; first-run rule scores are listed separately. "
                "The baseline was frozen before its first run on these sets.",
    }
    return summary, sets


def pct(m):
    return f"{m['correct']}/{m['total']} ({m['accuracy']:.0%})" if m["accuracy"] is not None else "—"


def write_report(summary, sets):
    first = summary["rules_first_run_exact"]
    lines = [
        "# Rule-based grounding vs dependency-parse baseline", "",
        "WordWorld drives the world with hand-written grounding rules (`backend/parser.py`). This report measures them against a "
        "grammar-driven alternative, `backend/dependency_baseline.py`, which reads the same actions from spaCy's dependency arcs "
        "(dobj, nummod, amod, prep/pobj, conj) using only the shared vocabulary, with no hand-written phrase patterns.", "",
        "## Method and caveats", "",
        f"- **Commands:** {summary['commands']} labelled commands: the 50-command development set, the held-out set and fresh sets v2–v10.",
        "- **Scoring:** identical field definitions to `tests/evaluate_heldout.py`. Exact match compares every field of the ordered action list.",
        "- **The rules have seen these sets.** After each set's first run, the rule parser was improved using its failures, so rule retest scores "
        f"are optimistic. Their recorded **first-run** exact match on the {first['sets']} frozen sets was **{first['correct']}/{first['total']} ({first['correct'] / first['total']:.0%})**.",
        f"- **The baseline has not.** It was written against separate example sentences and frozen (SHA-256 `{summary['baseline_sha256'][:12]}…`) "
        "before its first run here; it is not tuned on these results.",
        "- Fresh set v11 tests edits and cross-request references. Its context cases give the rules what the previous command touched; "
        "the baseline cannot use that context, which is part of what is being compared.",
        "- Both are implementation-aware, hand-authored diagnostics, not independent accuracy estimates.", "",
        "## Overall", "",
        "| Metric | Rules (retest) | Dependency baseline |", "|---|---|---|",
        *[f"| {field.replace('_', ' ')} | {pct(summary['rules'][field])} | {pct(summary['baseline'][field])} |" for field in FIELDS],
        f"| identical action lists | {summary['agreement']:.0%} of commands | |", "",
        "## By set", "",
        "| Set | Rules exact (retest) | Rules exact (first run) | Baseline exact | Baseline spatial |", "|---|---|---|---|---|",
        *[f"| {s['name']} | {pct(s['rules']['exact_match'])} | {s['rules_first_run_exact']['correct']}/{s['rules_first_run_exact']['total']} | "
          f"{pct(s['baseline']['exact_match'])} | {pct(s['baseline']['spatial'])} |" if s["rules_first_run_exact"] else
          f"| {s['name']} | {pct(s['rules']['exact_match'])} | (development set) | {pct(s['baseline']['exact_match'])} | {pct(s['baseline']['spatial'])} |"
          for s in sets], "",
        "## Reading the results", "",
        "The baseline is competitive on short, canonical commands (the development and held-out sets) but falls to single digits on the later "
        "fresh sets, which were written to probe counted partitions, totals, remainders, post-noun clauses and references. Dependency arcs "
        "locate the verb, its object and its prepositional phrases well; they do not say how a total splits into colored groups, which "
        "mention a pronoun means, or that a mention after 'keep' is protected rather than created. That missing layer is what the "
        "hand-written grounding rules supply, and it is why the world is driven by the rules while spaCy provides annotations.", "",
        "Even against the rules' **first-run** scores, which the rules had never seen, the gap stays large.", "",
        "## Where they differ", "",
        "Examples where only the baseline is right show phrasings the rules still miss; examples where only the rules are right show what "
        "dependency arcs alone do not capture (partitions, totals, remainders, references, negated or protected mentions).", "",
    ]
    rows = [r for s in sets for r in s["cases"]]
    for title, condition in [("Only the baseline is exactly right", lambda r: r["baseline_score"]["exact_match"] and not r["rules_score"]["exact_match"]),
                             ("Only the rules are exactly right (first 25)", lambda r: r["rules_score"]["exact_match"] and not r["baseline_score"]["exact_match"])]:
        picked = [r for r in rows if condition(r)]
        lines += [f"### {title}: {len(picked)}", ""]
        for r in picked[:25]:
            lines += [f"- **{r['id']}** “{r['text']}”", f"  - expected `{json.dumps(r['expected'])}`",
                      f"  - rules `{json.dumps(r['rules'])}`", f"  - baseline `{json.dumps(r['baseline'])}`"]
        lines.append("")
    lines += ["Full per-command predictions: `evaluation/results/extractor_comparison.json`. Regenerate with "
              "`python -m tests.compare_extractors`; CI runs it with `--check`."]
    return "\n".join(lines) + "\n"


def main():
    args = argparse.ArgumentParser()
    args.add_argument("--check", action="store_true", help="Fail if backend/extractor_scores.json differs from a fresh run")
    options = args.parse_args()
    summary, sets = run()
    text = json.dumps(summary, indent=2) + "\n"
    if options.check:
        saved = SUMMARY.read_text(encoding="utf-8") if SUMMARY.exists() else ""
        if saved != text:
            print("backend/extractor_scores.json is stale; run `python -m tests.compare_extractors` and commit the result.")
            sys.exit(1)
        print("Extractor comparison is current.")
        return
    # Explicit LF so files written on Windows match the ones CI compares against.
    SUMMARY.write_text(text, encoding="utf-8", newline="\n")
    RESULTS.write_text(json.dumps({"summary": summary, "sets": sets}, indent=2) + "\n", encoding="utf-8", newline="\n")
    REPORT.write_text(write_report(summary, sets), encoding="utf-8", newline="\n")
    for field in FIELDS:
        print(f"{field:20} rules {pct(summary['rules'][field]):>18}   baseline {pct(summary['baseline'][field]):>18}")
    print(f"identical action lists: {summary['agreement']:.0%}")


if __name__ == "__main__":
    main()
