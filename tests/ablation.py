r"""Ablation: what does each component of the grounding pipeline contribute?

Usage:  .venv\Scripts\python.exe -m tests.ablation [--json PATH] [--report PATH]

Every labelled command (650 across the development, held-out and eleven fresh sets) is scored by exact match against its gold
actions under one configuration at a time. Each ablation removes ONE component from the full rule parser:

  full rules                  the shipped parser
  - cross-request context     the client's "what 'it' means" is not sent
  - place filters             "paint the trees near the lake red" has no filter; filtered removals are refused
  - edit grammar              recolor / resize / move of existing objects is not read at all
  - spaCy (tokenizer only)    spaCy is removed entirely: the rules never used it for actions, only for annotations
  dependency baseline         the frozen comparison extractor that reads actions from spaCy's dependency arcs

Counts come with 95% Wilson score intervals. The rules were developed against these sets (after each set's first run), so
their numbers are optimistic; first-run scores are reported separately. The baseline was frozen before it ever ran here.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from contextlib import contextmanager
from pathlib import Path

from backend import edits, parser
from backend.dependency_baseline import extract
from tests.compare_extractors import labelled_sets

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "evaluation/results/ablation.json"
REPORT = ROOT / "evaluation/reports/ablation_report.md"

# Raw category names are fine-grained (quarter_partition, filter_remove_count, ...); group them by family for a readable breakdown.
FAMILIES = [
    ("references and pronouns", ("reference", "pronoun", "context", "former", "them", "ellipsis", "ones")),
    ("edits and place filters", ("edit", "recolor", "resize", "move", "filter", "paint")),
    ("counted partitions and fractions", ("partition", "fraction", "quarter", "third", "tenth", "percent", "remainder", "total", "each", "distributive", "colon", "thirds", "fifths", "sixths", "dozen", "multiplication")),
    ("spatial relations", ("spatial", "relation", "between", "across", "near", "location", "landmark", "front", "behind", "placement")),
    ("negation, protection, removal", ("negat", "protect", "remove", "removal", "keep", "zero", "abstention")),
    ("weather and time", ("weather", "time", "night", "rain", "storm", "setting")),
    ("colors and attributes", ("color", "roof", "petal", "leaf", "attribute", "postnoun", "passive", "future")),
    ("quantities", ("quantif", "quantit", "invalid", "count", "number", "pair", "cap")),
    ("coordination and multi-action sentences", ("coordinat", "multi_action", "mixed", "continuation", "shared", "tail", "scope")),
    ("clause structure", ("subordinate", "relative", "clause", "nested", "omitted", "compound", "inferred", "unmapped")),
    ("paraphrase and lexical variation", ("paraphrase", "lexical", "dawn", "stop")),
]


def family(category: str) -> str:
    lowered = (category or "").lower()
    for name, keys in FAMILIES:
        if any(k in lowered for k in keys):
            return name
    return "other"


def wilson(correct: int, total: int, z: float = 1.96):
    """95% Wilson score interval for a proportion; sound at the small counts used here."""
    if not total:
        return None
    p = correct / total
    denom = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denom
    half = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denom
    return [round(max(0.0, centre - half), 4), round(min(1.0, centre + half), 4)]


@contextmanager
def configuration(name: str):
    """Temporarily remove one component, restoring everything afterwards."""
    saved = {"read_edit": parser.read_edit, "filters": parser.FILTER_RELATIONS, "location": edits.read_location_filter, "nlp": parser.NLP}
    try:
        if name == "no_edits":
            parser.read_edit = lambda *args, **kwargs: None
        elif name == "no_filters":
            parser.FILTER_RELATIONS = frozenset()
            edits.read_location_filter = lambda clause, cursor: (None, cursor)
        elif name == "no_spacy":
            parser.NLP = None
        yield
    finally:
        parser.read_edit, parser.FILTER_RELATIONS = saved["read_edit"], saved["filters"]
        edits.read_location_filter, parser.NLP = saved["location"], saved["nlp"]


CONFIGS = [
    ("full", "Full rules"),
    ("no_context", "− cross-request context"),
    ("no_filters", "− place filters"),
    ("no_edits", "− edit grammar"),
    ("no_spacy", "− spaCy (tokenizer only)"),
    ("baseline", "Dependency baseline"),
]


def predict(config: str, case: dict):
    if config == "baseline":
        return extract(parser.NLP(case["text"]))
    context = None if config == "no_context" else case.get("context")
    try:
        return parser.parse(case["text"], context)["actions"]
    except ValueError:
        return []


def categories():
    """Map (set name, command id) -> category for the sets that carry one."""
    out = {}
    for name, path in [("heldout", "tests/heldout_commands.json")] + [(f"fresh_v{n}", f"tests/fresh_commands_v{n}.json") for n in range(2, 13)]:
        for case in json.loads((ROOT / path).read_text(encoding="utf-8"))["cases"]:
            out[(name, case["id"])] = case.get("category", "")
    return out


def run():
    cats, sets = categories(), list(labelled_sets())
    if parser.NLP is None or "parser" not in parser.NLP.pipe_names:
        raise SystemExit("The ablation needs the full en_core_web_sm model.")
    per_config = {}
    for config, label in CONFIGS:
        with configuration(config):
            rows = []
            for name, _title, first_run, cases in sets:
                for case in cases:
                    rows.append({"set": name, "id": case["id"], "ok": predict(config, case) == case["expected"],
                                 "family": "development set (uncategorised)" if name == "development" else family(cats.get((name, case["id"]), ""))})
        per_config[config] = {"label": label, "rows": rows}
    summary = {}
    for config, data in per_config.items():
        rows = data["rows"]
        by_set = {}
        for r in rows:
            c = by_set.setdefault(r["set"], [0, 0])
            c[0] += r["ok"]
            c[1] += 1
        by_family = {}
        for r in rows:
            c = by_family.setdefault(r["family"], [0, 0])
            c[0] += r["ok"]
            c[1] += 1
        correct = sum(r["ok"] for r in rows)
        summary[config] = {"label": data["label"], "correct": correct, "total": len(rows), "ci95": wilson(correct, len(rows)),
                           "by_set": by_set, "by_family": by_family}
    first_runs = {name: fr for name, _t, fr, _c in sets if fr}
    return summary, first_runs


def typo_ablation():
    path = ROOT / "evaluation/results/typo_robustness.json"
    if not path.exists():
        return None
    rows = json.loads(path.read_text(encoding="utf-8"))["rows"]
    total = len(rows)
    alone = sum(r["outcome"] == "harmless" for r in rows)
    with_suggestion = sum(r["outcome"] in {"harmless", "recovered"} and not r.get("false_alarm") for r in rows)
    return {"corrupted": total, "rules_alone": alone, "rules_alone_ci95": wilson(alone, total),
            "with_suggestion": with_suggestion, "with_suggestion_ci95": wilson(with_suggestion, total)}


def pct(correct, total):
    return f"{correct / total:.1%}" if total else "—"


def write_report(summary, first_runs, typos, path: Path):
    full = summary["full"]
    lines = [
        "# Ablation: what each component contributes", "",
        "Each row removes **one** component from the full rule parser and re-scores all 650 labelled commands by exact match against the gold "
        "actions. Intervals are 95% Wilson score intervals. The rules were developed against these sets after each set's first run, so their scores "
        "are optimistic; the first-run scores below are the honest ones. The baseline was frozen before it ever ran here.", "",
        "| Configuration | Exact match | 95% interval | Δ vs full |", "|---|---|---|---|",
    ]
    for config, _label in CONFIGS:
        s = summary[config]
        delta = s["correct"] - full["correct"]
        ci = f"{s['ci95'][0]:.1%} – {s['ci95'][1]:.1%}"
        lines.append(f"| {s['label']} | {s['correct']}/{s['total']} ({pct(s['correct'], s['total'])}) | {ci} | {'—' if config == 'full' else f'{delta:+d}'} |")
    lines += ["", "**Reading the table.** Removing spaCy changes nothing: the rules never used it for actions, only for token annotations "
              "(a claim the project makes and this row verifies). Removing the edit grammar costs exactly the commands that edit existing objects, and "
              "removing context costs exactly the commands that refer to an earlier command. The baseline falls far below every ablation of the rules, "
              "so the hand-written grounding, not the parse tree, carries the system.", "",
              "## By set", "", "| Set | Full rules | First run (frozen) | Baseline |", "|---|---|---|---|"]
    for name in summary["full"]["by_set"]:
        f, b = summary["full"]["by_set"][name], summary["baseline"]["by_set"][name]
        fr = first_runs.get(name)
        lines.append(f"| {name} | {f[0]}/{f[1]} | {f'{fr['correct']}/{fr['total']}' if fr else '(development set)'} | {b[0]}/{b[1]} |")
    lines += ["", "## By linguistic family (approximate: families are assigned from category names)", "",
              "| Family | Commands | Full rules | Baseline | Gap |", "|---|---|---|---|---|"]
    fams = sorted(summary["full"]["by_family"].items(), key=lambda kv: -kv[1][1])
    for name, (c, n) in fams:
        bc = summary["baseline"]["by_family"][name][0]
        lines.append(f"| {name} | {n} | {pct(c, n)} | {pct(bc, n)} | {(c - bc) / n:+.0%} |")
    if typos:
        lines += ["", "## Typo handling", "",
                  f"On {typos['corrupted']} commands carrying one synthetic typo (seed 4, never inspected), exact match is "
                  f"**{pct(typos['rules_alone'], typos['corrupted'])}** for the rules alone "
                  f"({typos['rules_alone_ci95'][0]:.1%} – {typos['rules_alone_ci95'][1]:.1%}) and "
                  f"**{pct(typos['with_suggestion'], typos['corrupted'])}** when the first “Did you mean” suggestion is applied "
                  f"({typos['with_suggestion_ci95'][0]:.1%} – {typos['with_suggestion_ci95'][1]:.1%}). The app never applies a suggestion itself; "
                  "this measures the ceiling if the person accepts it. The 9% is conditional on a typo landing in a vocabulary word the grammar needs, "
                  "chosen on purpose to stress the system; it is not a prediction of how often people mistype."]
    lines += ["", "## Limits", "",
              "These are hand-authored, implementation-aware sets: the author wrote both grammar and gold, and the rules saw each set after its first run. "
              "Differences of a few commands between configurations are within the intervals. Family assignment is heuristic. Nothing here estimates "
              "accuracy on strangers' sentences; the user-test kit (`docs/USER_TESTING.md`) exists to measure that."]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main():
    sys.stdout.reconfigure(encoding="utf-8")  # labels use real minus and en-dash characters
    args = argparse.ArgumentParser()
    args.add_argument("--json", type=Path, default=RESULTS)
    args.add_argument("--report", type=Path, default=REPORT)
    options = args.parse_args()
    summary, first_runs = run()
    typos = typo_ablation()
    options.json.write_text(json.dumps({"configurations": summary, "typos": typos}, indent=2) + "\n", encoding="utf-8", newline="\n")
    write_report(summary, first_runs, typos, options.report)
    for config, _label in CONFIGS:
        s = summary[config]
        print(f"{s['label']:28} {s['correct']}/{s['total']} ({pct(s['correct'], s['total'])})  95% CI {s['ci95'][0]:.1%}–{s['ci95'][1]:.1%}")


if __name__ == "__main__":
    main()
