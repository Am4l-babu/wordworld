"""Summarize post-noun fixes, three development retests and frozen round four."""
import hashlib
import json
from pathlib import Path

from tests.evaluate_heldout import pipeline_fingerprint

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
read = lambda name: json.loads((HERE/name).read_text(encoding='utf-8'))
before = [read(name) for name in ['heldout_retest_v3.json','fresh_v2_retest_v3.json','fresh_results_v3.json']]
current = [read(name) for name in ['heldout_retest_v4.json','fresh_v2_retest_v4.json','fresh_v3_retest_v4.json']]
fresh = read('fresh_results_v4.json')
pipeline, _ = pipeline_fingerprint()
for report in current + [fresh]:
    assert report['pipeline_sha256_before'] == report['pipeline_sha256_after'] == pipeline
    assert report['parser_unchanged']
for old, report in zip(before,current):
    assert old['dataset_sha256'] == report['dataset_sha256']
    assert [(c['id'],c['text'],c['expected_actions']) for c in old['cases']] == [(c['id'],c['text'],c['expected_actions']) for c in report['cases']]
assert fresh['matches_frozen_parser']
assert hashlib.sha256((ROOT/'tests/fresh_commands_v4.json').read_bytes()).hexdigest() == fresh['dataset_sha256']


def score(report, key='exact_match'):
    m = report['metrics'][key]
    return f"{m['correct']}/{m['total']} ({m['accuracy']:.1%})"


lines = [
    '# WordWorld post-noun and coordination fixes — 15 October 2026', '',
    f"**Three saved-set retests: {', '.join(score(r) for r in current)}. Fourth fresh set: {score(fresh)}.**", '',
    'All five previously observed target errors now pass: F46 (blue roof), G41 (orange roof), G42 (whose roof is green), G49 (houses, three of them), and G50 (two small and three large houses). Historical labels and results were preserved.', '',
    'The fourth sample was hand-authored and frozen before its first parser execution, including expected actions, scopes, and backend source hashes. There are no normalized exact overlaps with the four earlier datasets (the development 50 and three diagnostic sets), Python regression string literals, browser smoke-test literals or README lines at freeze time. Similar grammar is intentional. The author saw the implementation and earlier failures; this is a diagnostic sample, not an independent human-labeled benchmark or random real-user accuracy estimate.', '',
    '## Changes and scope', '',
    '- Adjacent post-noun colors attach to the source object: `with a blue roof`, `whose roof is green`, `that/which is pink`, and corresponding tree leaves/foliage and flower petals. These use existing visible color fields. Shared post-noun colors apply to separately counted coordinated groups.',
    '- Appositive quantities such as `houses, three of them`, `trees, five in total`, and `half a dozen altogether` are read before creation. The appositive `them` is consumed as part of the quantity, not as an extra action/reference. Final counts feed reference resolution and obey the existing 16-per-action cap.',
    '- Shared-noun coordination no longer needs colors: `two small and three large houses` becomes two add actions, with counts two and three. Comma lists, mixed colored/uncolored groups, shared placement, and per-group negation work. Each group needs an explicit count or article. Numeric conjunctions such as `one hundred and two` remain intact.',
    '- Contradictory prefix/post-noun counts or colors, ambiguous counts, negative/fractional quantities, missing group quantities, and unsupported color/part mappings abstain with notices. Zero groups add nothing. Repeated identical colors/counts are allowed.',
    '- Post-noun attributes stop at other subjects and placement phrases. Landmark attributes cannot bleed into following source objects; they do not select landmarks by color. The API and action schema stay compatible with the existing frontend. spaCy supplies annotations; action grounding remains rule based.', '',
    '**Limits:** Small/large are group descriptors only; size rendering is not implemented or scored. This is bounded grammar, not general post-noun English: the new sample still fails `painted blue`, nested roof clauses, `exactly five`, `five in all`, `ones`, group multiplication and relative-clause coordination. No backend or gold-label changes were made after observing the fourth-set predictions.', '',
    '## Verification', '',
    '| Check | Result |', '|---|---|',
    '| Python parser/API tests | 223 passed; 53 new regression cases |',
    '| Original development 50 | 50/50 exact matches |',
    '| Scene/preview unit tests | 16 passed |',
    '| Desktop/mobile Chromium integration | 18 passed |',
    '| React production build | Passed |',
    '| Local servers | FastAPI health OK with spaCy; Vite HTTP 200 |', '',
    'The new browser flow verifies three new blue roofs, five new purple-foliage trees from two count groups, exact inline quantity/color spans, and creation followed by reference removal preserving older houses. Undo/redo and existing object manipulations also pass. Both desktop and mobile screenshots were inspected: `.runtime/postnoun-fixes-desktop.png` and `.runtime/postnoun-fixes-mobile.png`.', '',
    '## Results', '',
    '| Set | Previous round | Current round | Interpretation |', '|---|---:|---:|---|',
]
for i,(old,report) in enumerate(zip(before,current),1):
    lines.append(f'| Diagnostic set {i} | {score(old)} | {score(report)} | Same frozen labels; development retest |')
lines += [f'| Fourth fresh 50 | Not run previously | {score(fresh)} | First predictions after label/code freeze |', '',
    '| Metric | Set 1 retest | Set 2 retest | Set 3 retest | New set 4 |', '|---|---:|---:|---:|---:|']
for key,label in [('intent','Intent sequence'),('entity_count_color','Objects/counts/colors'),('spatial','Spatial fields on gold-spatial commands'),('settings','Settings on gold-setting commands')]:
    lines.append('| '+label+' | '+' | '.join(score(r,key) for r in current+[fresh])+' |')
lines += ['',
    'The fresh set has **40/40 core matches and 0/10 broader probes**. Core includes two zero/negative-count refusal cases, one deliberately informal phrase within the implemented grammar, and one named-type landmark case that does not test color filtering. Its overall 80% must be reported together with this split. Different sets have different distributions; the fresh score is not a paired before/after comparison.', '',
    'Exact match requires every field of every ordered action dictionary. Field metrics are per-command sequence comparisons, not token scores. The object metric includes matching empty typed-action lists for pure settings. Spatial and setting denominators are their gold-bearing subsets. Parser scores do not validate scene geometry or cross-request context.', '',
    '## Remaining NLP errors', '',
    'The fourth sample has 10 errors and no exceptions. Four failures (H44–H46 and H50) emit partial actions without any notice; these need explicit detection as well as expanded grammar.', '',
    '| Priority / pattern | Cases | Observed problem |', '|---|---|---|',
    '| Quantity modifiers and tails | H42, H45, H47 | `exactly five`, `two groups of three`, and `five in all` create one object instead of five/six. |',
    '| Ellipsis and coordinated relative clauses | H44, H46 | `three large ones` and `and three that are yellow` lose the entire second group without a notice. |',
    '| More varied part-color clauses | H41, H43 | `roofs painted blue` and `a roof that is yellow` abstain with notices. |',
    '| Direction paraphrases | H48 | `northern side of the pond` abstains rather than placing above the lake. |',
    '| Subordinate creation | H49 | Preservation swallows `while planting three trees`; no trees are added. |',
    '| Weather synonyms | H50 | `no precipitation` fails to clear weather; only day is applied, without notice. |', '',
    'The earlier sets retain eight errors: F35 (daylight), F48 (while adding), F50 (construct); G43 (that crosses), G44 (construct), G45 (while building), G46 (without any rain), G47 (east side of). No new exact-match regressions appeared on the three saved samples.', '',
    '## All 50 fresh commands', '', '| ID | Scope | Result | Command |', '|---|---|---|---|',
]
for case in fresh['cases']:
    lines.append(f"| {case['id']} | {case['scope']} | {'PASS' if case['exact_match'] else 'FAIL'} | {case['text']} |")
for title, report in [('Fourth-set failures',fresh),('Second-set remaining failures',current[1]),('Third-set remaining failures',current[2])]:
    lines += ['', f'## {title}', '']
    for c in report['cases']:
        if c['exact_match']:
            continue
        lines += [f"### {c['id']}: {c['text']}", '', 'Expected:', '', '```json',
            json.dumps(c['expected_actions'],indent=2,ensure_ascii=False), '```', '', 'Actual:', '', '```json',
            json.dumps(c['predicted_actions'],indent=2,ensure_ascii=False), '```', '',
            'Notices: '+('; '.join(c['warnings']) or 'None.'), '']
lines += ['## Reproduce', '', 'From the project root:', '', '```powershell',
    '.\\.venv\\Scripts\\python.exe -m pytest -q tests',
    '.\\.venv\\Scripts\\python.exe -m tests.evaluate',
    '.\\.venv\\Scripts\\python.exe -X utf8 -m tests.evaluate_heldout --allow-parser-change --output evaluation/heldout_retest_v4.json']
for i,report in [(2,current[1]),(3,current[2]),(4,fresh)]:
    output = f'evaluation/fresh_v{i}_retest_v4.json' if i < 4 else 'evaluation/fresh_results_v4.json'
    lines.append(f'.\\.venv\\Scripts\\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v{i}.json --dataset-sha256 {report["dataset_sha256"]} '+('--allow-parser-change ' if i < 4 else '')+f'--output {output}')
lines += ['.\\.venv\\Scripts\\python.exe -X utf8 -m evaluation.write_postnoun_report', '```', '',
    'From `frontend/`, with the local servers running: `npm test`, `npm run test:e2e`, `npm run build`.', '',
    'Labels: `tests/fresh_commands_v4.json`. Complete predictions/notices: `evaluation/fresh_results_v4.json`. Three retests: `evaluation/heldout_retest_v4.json`, `evaluation/fresh_v2_retest_v4.json`, `evaluation/fresh_v3_retest_v4.json`. Regression source: `tests/test_postnoun_fixes.py` and `frontend/tests/browser/smoke.spec.js`.', '',
    f"Parser SHA256: `{fresh['parser_sha256_before']}`.",
    f"Backend pipeline SHA256: `{pipeline}`.",
    f"Fourth dataset SHA256: `{fresh['dataset_sha256']}`.", '',
    'The frozen dataset records per-file source hashes and the uniqueness-check input hashes. All four evaluations verified the same unchanged backend pipeline before and after prediction. The new dataset builder refuses overwriting labels; fresh evaluation refuses a changed pipeline. Once this sample informs future rule changes, use a separate result file marked as a development retest and a newly frozen sample for another fresh-command claim.', '',
]
assert sum(not c['exact_match'] and not c['warnings'] for c in fresh['cases']) == 4
out = HERE/'postnoun_fixes_report.md'
out.write_text('\n'.join(lines),encoding='utf-8')
print(out)
