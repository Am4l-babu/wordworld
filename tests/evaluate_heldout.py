r"""Evaluate the frozen new-command set without updating the parser or labels.

Usage: .venv\Scripts\python.exe -m tests.evaluate_heldout
Expected language errors are data in the report, not pytest failures.
"""
from collections import Counter, defaultdict
import argparse
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform

ROOT = Path(__file__).resolve().parents[1]
DATASET = Path(__file__).with_name("heldout_commands.json")
RESULTS = ROOT / "evaluation/heldout_results.json"
FROZEN_DATASET_SHA256 = "d372d2d85208319439929068902779ba4ea9144722caea783a8c792bcbd7a224"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pipeline_fingerprint():
    files = {str(path.relative_to(ROOT)).replace('\\', '/'): sha256(path) for path in sorted((ROOT/'backend').glob('*.py'))}
    digest = hashlib.sha256(json.dumps(files, sort_keys=True).encode('utf-8')).hexdigest()
    return digest, files


def evaluate(dataset_path=DATASET, output_path=RESULTS, expected_sha256=FROZEN_DATASET_SHA256, allow_parser_change=False):
    dataset_sha = sha256(dataset_path)
    if dataset_sha != expected_sha256:
        raise RuntimeError("The frozen labels changed; use a newly versioned evaluation.")
    dataset = json.loads(dataset_path.read_text(encoding="utf-8"))
    if len(dataset["cases"]) != 50:
        raise RuntimeError("This evaluation requires exactly 50 commands.")
    parser_before = sha256(ROOT / "backend/parser.py")
    pipeline_before, source_files = pipeline_fingerprint()
    matches_baseline = parser_before == dataset["parser_sha256_before"] and ('pipeline_sha256_before' not in dataset or pipeline_before == dataset['pipeline_sha256_before'])
    if not matches_baseline and not allow_parser_change:
        raise RuntimeError("Parser differs from the frozen baseline; do not reuse this baseline accuracy claim.")
    if (not matches_baseline or dataset_path.resolve() != DATASET.resolve()) and output_path.resolve() == RESULTS.resolve():
        raise RuntimeError("Use a separate output file; preserve the original evaluation results.")
    # Import only after dataset and parser identity have been verified.
    from backend.parser import NLP_STATUS, parse
    rows = []
    categories = defaultdict(lambda: {"correct": 0, "total": 0})
    scopes = defaultdict(lambda: {"correct": 0, "total": 0})
    counters = Counter()
    spatial_total = settings_total = 0
    project_objects = lambda actions: [(a.get("action"), a.get("type"), a.get("count"), a.get("color")) for a in actions if a.get("type")]
    project_spatial = lambda actions: [(a.get("type"), a.get("relation"), a.get("target"), a.get("targets")) for a in actions if a.get("type")]
    project_settings = lambda actions: [(a.get("key"), a.get("value")) for a in actions if a.get("action") == "setting"]
    for case in dataset["cases"]:
        error = None
        try:
            output = parse(case["text"])
        except Exception as exc:
            output = {"actions": [], "warnings": []}
            error = f"{type(exc).__name__}: {exc}"
        predicted, expected = output["actions"], case["expected_actions"]
        exact = error is None and predicted == expected
        intent = error is None and [a.get("action") for a in predicted] == [a["action"] for a in expected]
        objects = error is None and project_objects(predicted) == project_objects(expected)
        counters["exact_match"] += exact
        counters["intent"] += intent
        counters["entity_count_color"] += objects
        spatial = settings = None
        if any(a.get("relation") for a in expected):
            spatial_total += 1
            spatial = error is None and project_spatial(predicted) == project_spatial(expected)
            counters["spatial"] += spatial
        if any(a["action"] == "setting" for a in expected):
            settings_total += 1
            settings = error is None and project_settings(predicted) == project_settings(expected)
            counters["settings"] += settings
        for dimension, bucket in [("category", categories), ("scope", scopes)]:
            bucket[case[dimension]]["total"] += 1
            bucket[case[dimension]]["correct"] += exact
        if exact:
            outcome = "correct"
        elif error:
            outcome = "exception"
        elif not predicted:
            outcome = "explicit_abstention" if output.get("warnings") else "silent_omission"
        elif not expected:
            outcome = "unrequested_actions"
        elif len(predicted) > len(expected):
            outcome = "extra_actions"
        elif len(predicted) < len(expected):
            outcome = "missing_actions"
        else:
            outcome = "wrong_fields"
        unexpected_remove_types = sorted({a.get("type") for a in predicted if a.get("action") == "remove"} - {a.get("type") for a in expected if a["action"] == "remove"})
        rows.append({**case, "predicted_actions": predicted, "warnings": output.get("warnings", []),
                     "exact_match": exact, "intent_correct": intent, "entity_count_color_correct": objects,
                     "spatial_correct": spatial, "settings_correct": settings,
                     "outcome": outcome, "unexpected_remove_types": unexpected_remove_types, "exception": error})
    parser_after = sha256(ROOT / "backend/parser.py")
    pipeline_after, _ = pipeline_fingerprint()
    if parser_before != parser_after or pipeline_before != pipeline_after:
        raise RuntimeError("Parser changed during evaluation; discard this run.")
    denominators = {"exact_match": 50, "intent": 50, "entity_count_color": 50, "spatial": spatial_total, "settings": settings_total}
    report = {
        "name": dataset["name"], "method": dataset["method"], "scope": dataset["scope"],
        "evaluation_kind": "frozen new-command evaluation" if matches_baseline else "retest after parser development; not unseen-command accuracy",
        "matches_frozen_parser": matches_baseline,
        "dataset_parser_sha256": dataset["parser_sha256_before"],
        "dataset_sha256": dataset_sha, "parser_sha256_before": parser_before,
        "parser_sha256_after": parser_after, "parser_unchanged": parser_before == parser_after,
        "pipeline_sha256_before": pipeline_before, "pipeline_sha256_after": pipeline_after,
        "source_files_sha256": source_files,
        "runtime": {"python": platform.python_version(), "spacy": version("spacy"), "en_core_web_sm": version("en-core-web-sm"), "annotations": NLP_STATUS, "grounding": "rules"},
        "metric_definitions": {
            "exact_match": "Complete ordered action dictionaries match, including all emitted fields; per command over all 50.",
            "intent": "Ordered action-name sequence matches; per command over all 50. Does not validate entity or setting value.",
            "entity_count_color": "Ordered (action, type, count, color) tuples for all typed actions match, per command over all 50. Pure setting/no-op cases contribute empty typed-action lists.",
            "spatial": "Ordered (type, relation, target, targets) tuples for all typed actions match, on gold-spatial commands only. Extra subjects are penalized.",
            "settings": "Ordered (key, value) tuples for setting actions match, on gold-setting commands only.",
        },
        "metrics": {name: {"correct": counters[name], "total": total, "accuracy": counters[name] / total if total else None} for name, total in denominators.items()},
        "categories": dict(categories), "scopes": dict(scopes),
        "outcomes": dict(Counter(row["outcome"] for row in rows)),
        "cases": rows,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for name, metric in report["metrics"].items():
        accuracy = f"{metric['accuracy']:.1%}" if metric['accuracy'] is not None else 'N/A'
        print(f"{name}: {metric['correct']}/{metric['total']} = {accuracy}")
    print("\nScope groups:")
    for name, counts in report["scopes"].items():
        print(f"  {name}: {counts['correct']}/{counts['total']}")
    print("\nErrors:")
    for row in rows:
        if not row["exact_match"]:
            print(f"{row['id']} [{row['category']}] {row['text']}\n  expected: {json.dumps(row['expected_actions'], ensure_ascii=False)}\n  actual:   {json.dumps(row['predicted_actions'], ensure_ascii=False)}\n  notices:  {json.dumps(row['warnings'], ensure_ascii=False)}")
    print(f"\nParser unchanged during run: {report['parser_unchanged']}\nEvaluation kind: {report['evaluation_kind']}\nResults: {output_path}")
    return report


if __name__ == "__main__":
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument('--dataset', type=Path, default=DATASET)
    args.add_argument('--dataset-sha256', default=FROZEN_DATASET_SHA256)
    args.add_argument('--output', type=Path, default=RESULTS)
    args.add_argument('--allow-parser-change', action='store_true', help='Explicitly mark this run as a development retest, not unseen-command accuracy')
    options = args.parse_args()
    evaluate(options.dataset, options.output, options.dataset_sha256, options.allow_parser_change)
