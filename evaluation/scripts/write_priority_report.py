"""Render the priority fixes, original-set comparison, and second fresh set."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT/'evaluation'/'results'
REPORTS = ROOT/'evaluation'/'reports'
baseline = json.loads((HERE/'heldout_results.json').read_text(encoding='utf-8'))
retest = json.loads((HERE/'heldout_retest.json').read_text(encoding='utf-8'))
fresh = json.loads((HERE/'fresh_results_v2.json').read_text(encoding='utf-8'))
assert baseline['dataset_sha256'] == retest['dataset_sha256']
assert retest['parser_sha256_before'] == fresh['parser_sha256_before']
assert fresh['parser_sha256_before'] == fresh['parser_sha256_after']
assert hashlib.sha256((ROOT/'backend/parser.py').read_bytes()).hexdigest() == fresh['parser_sha256_before']
assert hashlib.sha256((ROOT/'tests/fresh_commands_v2.json').read_bytes()).hexdigest() == fresh['dataset_sha256']
assert [c['expected_actions'] for c in baseline['cases']] == [c['expected_actions'] for c in retest['cases']]


def metric_line(name, key):
    cells=[]
    for report in [baseline, retest, fresh]:
        metric=report['metrics'][key]
        cells.append(f"{metric['correct']}/{metric['total']} ({metric['accuracy']:.1%})")
    return f"| {name} | " + ' | '.join(cells) + ' |'


lines = [
    '# WordWorld priority fixes and fresh evaluation — 15 October 2026', '',
    '**Original diagnostic set: 35/50 → 46/50 (70% → 92%). Second fresh set: 40/50 (80%).**', '',
    'The original 50-command set is now a development/regression comparison set. Its gold labels and original 35/50 results were preserved; its retest is not an unseen-language result. The second set contains 50 newly authored commands with expected outputs frozen before their first execution on the final parser. There are no normalized exact overlaps with either previous 50-command set, Python regression string literals, browser smoke test strings, or README command lines.', '',
    'Both sets are hand-authored diagnostic samples. Their author saw the implementation and previous results; they are neither independently human-labeled nor randomly sampled from real users. They intentionally include broader capability probes. The old and new distributions differ, so 92% and 80% are not a paired before/after comparison. No parser changes or gold-label adjustments were made after observing second-round predictions.', '',
    '## Implemented fixes', '',
    '- Normalize curly apostrophes, common Unicode hyphens, and Unicode minus signs one character at a time, keeping original text offsets exact. Negated creation/removal/reset clauses are skipped; `not rain`, `not snow`, and `without rain/snow` map to clear weather.',
    '- Treat keep/leave/preserve/retain/protect clauses as non-mutating object mentions. Unsupported context/verb statements no longer imply creation merely because they mention a supported noun. Bare noun phrases remain supported.',
    '- Parse common cardinal words, pairs, dozens, half a dozen, and group multipliers. Enforce the 16-object action cap. Negative, fractional, disjunctive and recognized ambiguous quantities produce a notice instead of defaulting silently to one.',
    '- Attach initial location phrases to the following explicit action, with or without a comma. Extract their landmarks before considering action subjects, including two-target `between`. A shared initial phrase applies to coordinated subjects under one verb; an explicit new verb starts a new instruction. Unsupported filtered removal and multiple placement constraints are skipped with notices.',
    '- Highlight preserved object mentions in the inline explanation; make no-change responses explicit. Action grounding remains rule based; spaCy supplies token/grammar annotations.', '',
    '## Verification', '',
    '| Check | Result |', '|---|---|',
    '| Python parser/API regressions | 142 passed; 64 more than the original 78 |',
    '| Original 50-command development set | 50/50 exact matches |',
    '| Scene and offline-preview logic | 13 passed |',
    '| Desktop/mobile Playwright | 14 passed; includes negation, protected mentions, quantity phrases and initial-location rendering |',
    '| React production build | Passed |', '',
    'The new browser flow checks that a negated bridge command leaves the count unchanged, preserving houses/removing flowers keeps exactly two houses, and `Behind the lake, plant a pair of purple trees` adds two trees without adding a second lake. Screenshots are saved at `.runtime/parser-fixes-desktop.png` and `.runtime/parser-fixes-mobile.png`.', '',
    '## Accuracy', '',
    '| Metric | Original parser, first set | Updated parser, first-set retest | Updated parser, second fresh set |', '|---|---:|---:|---:|',
    metric_line('Full ordered action JSON', 'exact_match'),
    metric_line('Intent sequence', 'intent'),
    metric_line('Objects/counts/colors, all commands', 'entity_count_color'),
    metric_line('Spatial fields, gold-spatial subset', 'spatial'),
    metric_line('Time/weather values, gold-setting subset', 'settings'), '',
    'The first-set core subset improved from **35/44 to 44/44**. Its six capability probes improved from 0/6 to 2/6 after preservation/context handling was fixed. All four remaining first-set errors are H30–H32 (pronouns) and H38 (elliptical coordination).', '',
    'The second fresh set scored **40/40 core commands** and **0/10 broader capability probes**. Four failed commands emitted no parser notice. There were no parser exceptions. Counts clipped to 16 and invalid-quantity abstentions were labeled according to the existing action contract, before prediction.', '',
    'Metrics are per-command sequence comparisons. Exact match compares every action field and action order. The object metric includes matching empty object lists on pure-setting/no-op commands. Spatial and setting scores use their gold-bearing subsets. Existing landmarks are assumed; scene geometry and cross-request conversation state are not part of parser accuracy.', '',
    '## Remaining errors from the second fresh set', '',
    '| Priority | Pattern / cases | Observed behavior | Next fix |', '|---|---|---|---|',
    '| 1 | Unsupported relation paraphrase — F47 | `Put a bridge spanning the creek.` adds a bridge AND an unintended river; relation/target are missing. | Classify noun roles conservatively within each action and recognize relational paraphrases such as spanning, or abstain on unsupported modifiers. The current fixes do not guarantee absence of unintended creation for every English construction. |',
    '| 2 | Pronouns — F41–F43 | `it` and `them` lose the following placement/removal action. | Add scoped, typed reference resolution within an utterance. |',
    '| 3 | Omitted coordinated nouns — F44–F45 | Two differently colored groups collapse to the last group. | Expand coordinated count/color phrases into separate grounded actions. |',
    '| 4 | Post-noun attributes — F46 | `a house with a blue roof` loses blue. | Attach roof/color modifiers to the house rather than requiring color before the noun. |',
    '| 4 | Clause/verb paraphrases — F48, F50 | `while adding` loses the add action; `construct` abstains. | Recognize action-bearing subordinate clauses and expand safe verb aliases. |',
    '| 5 | Setting paraphrase — F35 | `daylight` does not set day. | Expand setting aliases while preserving negation scope. |', '',
    '## All 50 second-round commands', '', '| ID | Scope | Result | Command |', '|---|---|---|---|',
]
for case in fresh['cases']:
    lines.append(f"| {case['id']} | {case['scope']} | {'PASS' if case['exact_match'] else 'FAIL'} | {case['text'].replace('|', chr(92)+'|')} |")
lines += ['', '## Expected and actual outputs for fresh-set errors', '']
for case in fresh['cases']:
    if case['exact_match']:
        continue
    lines += [f"### {case['id']}: {case['text']}", '', f"Category: {case['category']}. Scope: {case['scope']}.", '']
    if case['label_note']:
        lines += ['Label rationale: '+case['label_note'], '']
    lines += ['Expected:', '', '```json', json.dumps(case['expected_actions'], indent=2, ensure_ascii=False), '```', '',
              'Actual:', '', '```json', json.dumps(case['predicted_actions'], indent=2, ensure_ascii=False), '```', '',
              'Notices: '+('; '.join(case['warnings']) or 'None.'), '']
lines += [
    '## Reproduce', '', 'From the project root:', '', '```powershell',
    '.\\.venv\\Scripts\\python.exe -m pytest -q tests',
    '.\\.venv\\Scripts\\python.exe -X utf8 -m tests.evaluate_heldout --allow-parser-change --output evaluation/results/heldout_retest.json',
    f".\\.venv\\Scripts\\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v2.json --dataset-sha256 {fresh['dataset_sha256']} --output evaluation/results/fresh_results_v2.json",
    '.\\.venv\\Scripts\\python.exe -X utf8 evaluation/scripts/write_priority_report.py', '```', '',
    'From `frontend/`, with API and Vite running: `npm test`, `npm run test:e2e`, and `npm run build`.', '',
    '- Original frozen labels: `tests/heldout_commands.json` (unchanged).',
    '- Original predictions: `evaluation/results/heldout_results.json` (unchanged).',
    '- First-set retest: `evaluation/results/heldout_retest.json`.',
    '- New frozen labels and development-input hashes: `tests/fresh_commands_v2.json`.',
    '- New predictions/notices: `evaluation/results/fresh_results_v2.json`.',
    '- Regression coverage: `tests/test_accuracy_fixes.py` and `frontend/tests/browser/smoke.spec.js`.', '',
    f"Final parser SHA256: `{fresh['parser_sha256_before']}`.",
    f"Second-set SHA256: `{fresh['dataset_sha256']}`.", '',
    'The parser hash is identical between the first-set retest and the second-set run, and before/after the fresh evaluation. The evaluator refuses modified labels and protects the original result file. If second-round failures guide future development, this set becomes a regression/comparison set; another new sample is needed for a future fresh-command claim.', '',
]
assert sum(not case['exact_match'] and not case['warnings'] for case in fresh['cases']) == 4
out=REPORTS/'priority_fixes_report.md'
out.write_text('\n'.join(lines), encoding='utf-8')
print(out)
