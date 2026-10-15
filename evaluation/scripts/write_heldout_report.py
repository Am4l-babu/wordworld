"""Render the recorded evaluation. Does not execute the parser or change gold."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DIRECTORY = ROOT / "evaluation" / "results"
REPORTS = ROOT / "evaluation" / "reports"
results = json.loads((DIRECTORY / "heldout_results.json").read_text(encoding="utf-8"))
dataset = ROOT / "tests/heldout_commands.json"
assert hashlib.sha256(dataset.read_bytes()).hexdigest() == results["dataset_sha256"]
assert results["parser_sha256_before"] == results["parser_sha256_after"]

category_names = {
    "lexical_grounding": "Aliases and familiar noun phrases",
    "spatial_grounding": "Post-noun spatial relations",
    "multi_action_scope": "Multiple actions and modifier scope",
    "settings": "Time/weather wording",
    "negation": "Negation, zero quantities and contrasts",
    "quantifiers": "New quantity expressions",
    "coreference": "Within-command pronoun reference",
    "fronted_relations": "Location phrase before the verb",
    "coordination_ellipsis": "Coordinated colors with an omitted noun",
    "protected_mentions": "Keep/leave-alone object mentions",
}
metric_names = {"exact_match": "Complete ordered action JSON", "intent": "Action-name sequence", "entity_count_color": "Object/action/count/color sequence, over all commands", "spatial": "Spatial fields on commands with a gold relation", "settings": "Time/weather values on commands with gold settings"}


def cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


lines = [
    "# WordWorld: 50 new commands — 15 October 2026", "",
    "**Result: 35/50 complete action matches (70.0%). The parser was not modified.**", "",
    "This is a new hand-authored diagnostic challenge set, frozen with expected action JSON before its first parser execution. All 50 commands are unique and have no normalized exact matches in the existing development JSON, Python test literals, browser smoke test literals, or README command lines. Similar grammatical constructions are intentionally represented; lexical/structural independence is not claimed.", "",
    "The author had already seen the implementation and development examples. This is not an independently human-labeled or randomly sampled benchmark, so 70% should not be presented as population/user-traffic accuracy. The six capability probes are identified in advance; some deliberately test documented limitations, notably pronouns. No gold labels or parser rules were tuned after observing predictions.", "",
    "## Accuracy", "", "| Metric | Correct / total | Accuracy |", "|---|---:|---:|",
]
for name, counts in results["metrics"].items():
    lines.append(f"| {metric_names[name]} | {counts['correct']}/{counts['total']} | {counts['accuracy']:.1%} |")
lines += ["", "Exact match requires every ordered action dictionary to match, including quantities, colors, relation targets and setting values. Field metrics are per-command sequence comparisons, not per-token accuracy. The all-command object metric includes matching empty object lists in pure-setting and intentional no-op cases. Spatial/setting metrics use their gold-bearing subsets and do not measure overall command correctness.", "",
          "| Preassigned scope | Exact matches | Accuracy |", "|---|---:|---:|"]
for name, counts in results["scopes"].items():
    lines.append(f"| {'Core commands' if name == 'core' else 'Capability probes'} | {counts['correct']}/{counts['total']} | {counts['correct']/counts['total']:.1%} |")
lines += ["", "There were **15 errors and no parser exceptions**. Twelve incorrect commands had no parser warning; the three pronoun failures did emit a notice. Landmarks were assumed to exist, and parsing was evaluated independently for each command. Scene geometry, whether a material color is rendered, and conversation history across requests were not scored.", "",
          "## Main remaining errors and fixes", "",
          "| Priority | Error pattern | Failed cases | Observed example | Suggested fix |", "|---|---|---|---|---|",
          "| 1 | Negation variants | H48, H49 | `Don’t add any bridges.` creates a bridge; `Make it not rain.` emits no action instead of clear weather. | Normalize Unicode apostrophes before matching (preserving original-span offsets), and interpret negation at the intent/setting level. |",
          "| 2 | Front-loaded location phrases | H33–H35 | `Near the lake, plant four trees.` creates an extra lake and loses the near relation. | Attach an initial prepositional phrase to the following action; classify its nouns as landmarks before clause splitting. |",
          "| 2 | Protected/context-only nouns | H43, H44 | `Keep the houses and remove the trees.` adds a house; `Leave the lake alone and add a bridge.` adds a lake. | Recognize preservation/context clauses; only action subjects should become creations. Avoid fallback creation for every recognized noun. |",
          "| 3 | Quantity vocabulary | H26–H29 | Eleven houses, a dozen flowers, a pair of rocks, and twelve cottages all become count 1. | Expand cardinal and quantifier phrases within the 16-object cap; warn rather than silently default on unrecognized quantities. |",
          "| 4 | Pronoun resolution | H30–H32 | `Build a house, then remove it.` only builds the house. | Track typed referents through actions within one utterance; use explicit ambiguity handling before extending to cross-request history. |",
          "| 5 | Elliptical coordination | H38 | `Build one red and one blue house.` produces only one blue house. | Expand coordinated modifier phrases into distinct noun phrases/actions while preserving each color and count. |", "",
          "Basic alias lookup, post-noun relations, and explicit mixed actions performed well on these examples. The failures mostly concern phrase attachment, scope and reference resolution. spaCy is installed and supplies annotations, but current action grounding is lexical/rule based; its dependency parse is not used to resolve these semantics.", "",
          "## Category breakdown", "", "| Category | Correct / total | Errors |", "|---|---:|---:|"]
for name, counts in results["categories"].items():
    lines.append(f"| {category_names[name]} | {counts['correct']}/{counts['total']} | {counts['total']-counts['correct']} |")
lines += ["", "## All 50 commands", "", "| ID | Scope | Result | Command |", "|---|---|---|---|"]
for row in results["cases"]:
    lines.append(f"| {row['id']} | {row['scope']} | {'PASS' if row['exact_match'] else 'FAIL'} | {cell(row['text'])} |")
lines += ["", "## Expected vs. actual for every failure", ""]
for row in results["cases"]:
    if row["exact_match"]:
        continue
    lines += [f"### {row['id']}: {row['text']}", "", f"Category: {category_names[row['category']]}. Scope: {row['scope']}. Outcome: {row['outcome']}.", ""]
    if row["label_note"]:
        lines += [f"Label rationale: {row['label_note']}", ""]
    lines += ["Expected:", "", "```json", json.dumps(row["expected_actions"], indent=2, ensure_ascii=False), "```", "", "Actual:", "", "```json", json.dumps(row["predicted_actions"], indent=2, ensure_ascii=False), "```", "", "Parser notices: " + ("; ".join(row["warnings"]) or "None."), ""]
lines += ["## Reproducibility and integrity", "",
          "From the project root, with the installed environment:", "", "```powershell", ".\\.venv\\Scripts\\python.exe -X utf8 -m tests.evaluate_heldout", ".\\.venv\\Scripts\\python.exe -X utf8 evaluation\\scripts\\write_heldout_report.py", "```", "",
          "The runner refuses changed gold labels or a parser whose source differs from the baseline captured before evaluation. Expected language errors remain in the result JSON; the script completes successfully when the evaluation itself ran. It does not silently rewrite the gold set or add these examples to the development tests.", "",
          "- Dataset: `tests/heldout_commands.json`", "- Full predictions and notices: `evaluation/results/heldout_results.json`", "- Prediction-free dataset construction: `tests/create_heldout_set.py`", "- Runner: `tests/evaluate_heldout.py`", "",
          f"- Frozen dataset SHA256: `{results['dataset_sha256']}`", f"- Parser SHA256 before: `{results['parser_sha256_before']}`", f"- Parser SHA256 after: `{results['parser_sha256_after']}`", "",
          "Runtime: " + ", ".join(f"{key}={value}" for key, value in results["runtime"].items()) + ".", "",
          "Once these failures guide parser changes, this set becomes a regression/comparison set. Author another fresh set for a future unseen-command accuracy claim.", ""]
assert sum(not row["exact_match"] and not row["warnings"] for row in results["cases"]) == 12
(REPORTS / "heldout_report.md").write_text("\n".join(lines), encoding="utf-8")
print(REPORTS / "heldout_report.md")
