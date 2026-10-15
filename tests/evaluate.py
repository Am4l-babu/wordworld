"""Full-action development evaluation. This set is not independent or held out."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys

from backend.parser import parse

GOLD = json.loads(Path(__file__).with_name("commands.json").read_text(encoding="utf-8"))


def evaluate(parser):
    hits = {key: 0 for key in ["intent", "entity_count_color", "spatial", "exact_match"]}
    failures = []
    spatial_total = 0
    for case in GOLD:
        predicted, gold = parser(case["text"])["actions"], case["actions"]
        hits["intent"] += [a["action"] for a in predicted] == [a["action"] for a in gold]
        fields = ("action", "type", "count", "color", "key", "value")
        project = lambda actions: [tuple(a.get(key) for key in fields) for a in actions]
        hits["entity_count_color"] += project(predicted) == project(gold)
        if any(a.get("relation") for a in gold):
            spatial_total += 1
            spatial = lambda actions: [(a.get("type"), a.get("relation"), a.get("target"), a.get("targets")) for a in actions if a.get("type")]
            hits["spatial"] += spatial(predicted) == spatial(gold)
        hits["exact_match"] += predicted == gold
        if predicted != gold:
            failures.append({"text": case["text"], "expected": gold, "predicted": predicted})
    totals = {key: spatial_total if key == "spatial" else len(GOLD) for key in hits}
    return {"set": "hand-written development regressions (not held out)", "metrics": {key: {"correct": hits[key], "total": totals[key], "accuracy": hits[key] / totals[key]} for key in hits}, "failures": failures}


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--parser-file", type=Path, help="Optional previous parser for a same-set comparison")
    args.add_argument("--json", type=Path, help="Save metrics and error cases")
    options = args.parse_args()
    parser = parse
    if options.parser_file:
        spec = importlib.util.spec_from_file_location("comparison_parser", options.parser_file)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        parser = module.parse
    report = evaluate(parser)
    for key, metric in report["metrics"].items():
        print(f"{key}: {metric['correct']}/{metric['total']} = {metric['accuracy']:.1%}")
    for failure in report["failures"]:
        print(f"FAIL: {failure['text']}\n  expected: {failure['expected']}\n  got: {failure['predicted']}")
    print("Hand-written development set; these scores do not measure unseen-command accuracy.")
    if options.json:
        options.json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    sys.exit(bool(report["failures"]))
