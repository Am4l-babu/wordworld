"""Record reference/coordination fixes and all three versioned evaluations."""
import hashlib
import json
from pathlib import Path

from tests.evaluate_heldout import pipeline_fingerprint

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
first_before = json.loads((HERE/'heldout_retest.json').read_text(encoding='utf-8'))
second_before = json.loads((HERE/'fresh_results_v2.json').read_text(encoding='utf-8'))
first = json.loads((HERE/'heldout_retest_v3.json').read_text(encoding='utf-8'))
second = json.loads((HERE/'fresh_v2_retest_v3.json').read_text(encoding='utf-8'))
fresh = json.loads((HERE/'fresh_results_v3.json').read_text(encoding='utf-8'))
pipeline, _ = pipeline_fingerprint()
assert first['dataset_sha256'] == first_before['dataset_sha256']
assert second['dataset_sha256'] == second_before['dataset_sha256']
assert first['pipeline_sha256_before'] == second['pipeline_sha256_before'] == fresh['pipeline_sha256_before'] == pipeline
assert fresh['pipeline_sha256_before'] == fresh['pipeline_sha256_after']
assert hashlib.sha256((ROOT/'tests/fresh_commands_v3.json').read_bytes()).hexdigest() == fresh['dataset_sha256']
for original, current in [(first_before,first),(second_before,second)]:
    assert [c['expected_actions'] for c in original['cases']] == [c['expected_actions'] for c in current['cases']]


def score(report, key='exact_match'):
    m=report['metrics'][key]
    return f"{m['correct']}/{m['total']} ({m['accuracy']:.1%})"


lines = [
    '# WordWorld reference and coordination fixes — 15 October 2026', '',
    f"**First-set retest: {score(first)}. Second-set retest: {score(second)}. Third fresh set: {score(fresh)}.**", '',
    'The previously evaluated sets are now regression/comparison sets. Their labels and original results were preserved. The third set contains 50 new commands and expected outputs frozen before any predictions, with no normalized exact overlap against all three previous sets, regression-test literals, browser smoke-test literals or README command lines. Similar grammar structures are intentionally represented.', '',
    'These are hand-authored diagnostic samples, not random real-user accuracy estimates or independently human-labeled benchmarks. The author saw the implementation and previous errors. The third set has 40 preassigned core cases and 10 broader grammar probes; some core cases intentionally expect conservative refusal of ambiguous or exhausted references. No parser/rule/label changes were made after observing the third-set results.', '',
    '## What changed', '',
    '- `spanning` and `crossing` ground to `across`. Their following nouns are landmarks. Unsupported connections between object nouns reject the instruction instead of creating extra nouns. The exact extra-river regression now emits only one bridge action with river as its target.',
    '- A new request-local reference context tracks creation groups, types, live counts and the action that introduced each group. `it` resolves the latest live singular introduction; `them` resolves the latest coordinated creation collection. Explicit new creation verbs reset collection focus; comma-separated subjects remain one collection. Settings preserve the referents; reset clears them. There is no cross-request or global conversation memory.',
    '- Pronouns support removal subjects and spatial landmarks. Partial removal of a homogeneous collection is bounded to that collection; subsequent pronouns see the remaining count. A partial selection from mixed types or singular `it` after a plural group abstains with a notice. Spatial `them` currently requires exactly two objects with `between`; other plural-spatial relations abstain.',
    '- Explicitly counted coordinated colors expand into separate actions, including comma lists, shared placement relations, group quantifiers and per-group negation. Number phrases such as `one hundred and two` retain their numeric conjunction. Ambiguous color coordination without separate counts abstains. Non-color coordination remains a limitation.',
    '- API `bindings` connect reference actions to their antecedent action indices. The frontend binds these to the actual new SVG object IDs, preserving unrelated older objects, including when the scene limit blocks a creation. Existing named-landmark behavior is unchanged. The action dictionaries remain compatible with the prior schema.',
    '- The inline explanation highlights references and displays their resolved types/counts. Action grounding remains deterministic and rule based; spaCy provides linguistic annotations.', '',
    '## Verification', '', '| Check | Result |', '|---|---|',
    '| Python parser/API regressions | 170 passed (28 additional cases) |',
    '| Original development 50 | 50/50 exact action matches |',
    '| Scene/preview tests | 16 passed, including reference ID/capacity guards |',
    '| Desktop/mobile Playwright | 16 passed |',
    '| React production build | Passed |', '',
    'The new browser flow checks that a bridge spanning a creek adds no river, a newly built then removed house does not remove the two starter houses, and two coordinated colored houses become the anchors of a tree placed between them. Screenshots: `.runtime/reference-fixes-desktop.png` and `.runtime/reference-fixes-mobile.png`.', '',
    '## Evaluations', '', '| Set | Before this round | After this round | Interpretation |', '|---|---:|---:|---|',
    f"| First diagnostic set | {score(first_before)} | {score(first)} | Same gold labels; development retest |",
    f"| Second diagnostic set | {score(second_before)} | {score(second)} | Same gold labels; development retest |",
    f"| Third fresh set | Not previously executed | {score(fresh)} | Gold frozen before first prediction |", '',
    '| Per-command metric | First-set retest | Second-set retest | Third fresh set |', '|---|---:|---:|---:|',
]
for key,label in [('intent','Intent sequence'),('entity_count_color','Objects/counts/colors'),('spatial','Spatial fields, gold-spatial subset'),('settings','Time/weather, gold-setting subset')]:
    lines.append(f'| {label} | {score(first,key)} | {score(second,key)} | {score(fresh,key)} |')
lines += [
    '', 'First-set scopes: 44/44 core and 6/6 probes. Second-set scopes: 40/40 core and 6/10 probes. Third-set scopes: **40/40 core and 1/10 probes**. Different sets have different distributions; the third-set score is not a paired before/after comparison.', '',
    'Exact match compares every field in every ordered action dictionary. Field metrics compare per-command sequences, not tokens. The object metric includes matching empty typed-action lists in pure-setting/no-op cases. Spatial/setting metrics use their gold-bearing subsets. Existing named landmarks are assumed; scene geometry and cross-request conversational reference are not part of parser accuracy.', '',
    '## Remaining errors', '',
    'The second set still fails F35 (`daylight`), F46 (post-noun roof color), F48 (`while adding`) and F50 (`construct`). These were not part of the current requested grammar changes.', '',
    'The third set has **9 exact-match errors and no parser exceptions**. Four errors emitted no parser notice. The unsupported finite relation `that crosses the river` and direction `east side of the lake` now abstain rather than create their landmarks.', '',
    '| Pattern | Third-set cases | Example / behavior |', '|---|---|---|',
    '| Post-noun attributes | G41–G42 | `a cottage with an orange roof` loses orange. |',
    '| Relation/direction paraphrases | G43, G47 | `that crosses` and `east side of` abstain; no extra river/lake is created. |',
    '| Creation/subordinate verb variants | G44–G45 | `construct` and `while building` lose the intended creation. |',
    '| Negated weather with a determiner | G46 | `without any rain` fails to clear weather; only day is applied. |',
    '| Quantity after the noun | G49 | `houses, three of them` creates one house instead of three. |',
    '| Coordination without colors | G50 | `two small and three large houses` keeps only the final three. |', '',
    'G48 passed: `those trees` explicitly names the object type and produces the correct two-target action. This does not establish general demonstrative or color-filtered reference support.', '',
    '## All 50 new commands', '', '| ID | Scope | Result | Command |', '|---|---|---|---|',
]
for c in fresh['cases']:
    lines.append(f"| {c['id']} | {c['scope']} | {'PASS' if c['exact_match'] else 'FAIL'} | {c['text']} |")
lines += ['', '## Fresh-set failures: expected and actual', '']
for c in fresh['cases']:
    if c['exact_match']:
        continue
    lines += [f"### {c['id']}: {c['text']}", '', f"Category: {c['category']}. Scope: {c['scope']}.", '']
    if c['label_note']:
        lines += ['Label rationale: '+c['label_note'], '']
    lines += ['Expected:', '', '```json', json.dumps(c['expected_actions'],indent=2,ensure_ascii=False), '```', '',
              'Actual:', '', '```json', json.dumps(c['predicted_actions'],indent=2,ensure_ascii=False), '```', '',
              'Notices: '+('; '.join(c['warnings']) or 'None.'), '']
lines += [
    '## Reproduce', '', 'From the project root:', '', '```powershell',
    '.\\.venv\\Scripts\\python.exe -m pytest -q tests',
    '.\\.venv\\Scripts\\python.exe -X utf8 -m tests.evaluate_heldout --allow-parser-change --output evaluation/heldout_retest_v3.json',
    '.\\.venv\\Scripts\\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v2.json --dataset-sha256 050f1f92dba55b89883ebd05c4dc074b287c230a65f33f3d12a7a321ee17042b --allow-parser-change --output evaluation/fresh_v2_retest_v3.json',
    f".\\.venv\\Scripts\\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v3.json --dataset-sha256 {fresh['dataset_sha256']} --output evaluation/fresh_results_v3.json",
    '.\\.venv\\Scripts\\python.exe -X utf8 -m evaluation.write_reference_report', '```', '',
    'From `frontend/`, with FastAPI and Vite running: `npm test`, `npm run test:e2e`, `npm run build`.', '',
    '- Third frozen labels: `tests/fresh_commands_v3.json`.',
    '- Third predictions, notices and per-case correctness: `evaluation/fresh_results_v3.json`.',
    '- Earlier-set retests: `evaluation/heldout_retest_v3.json`, `evaluation/fresh_v2_retest_v3.json`.',
    '- Main regressions: `tests/test_reference_fixes.py`, `frontend/tests/world.test.js`, `frontend/tests/browser/smoke.spec.js`.', '',
    f"Parser SHA256: `{fresh['parser_sha256_before']}`.",
    f"Backend pipeline SHA256: `{fresh['pipeline_sha256_before']}`.",
    f"Third dataset SHA256: `{fresh['dataset_sha256']}`.", '',
    'All backend Python source hashes, including the new reference module, were captured before and after each evaluation. The evaluator refuses changed labels/pipeline for a fresh run and protects historical baseline results. Once third-set errors guide future development, it becomes a regression/comparison set and a new sample is needed for another fresh-command claim.', '',
]
assert sum(not c['exact_match'] and not c['warnings'] for c in fresh['cases']) == 4
out=HERE/'reference_fixes_report.md'
out.write_text('\n'.join(lines),encoding='utf-8')
print(out)
