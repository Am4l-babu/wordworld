"""Preserve tenth-round first predictions and nine separate saved-set retests."""
import hashlib
import json
from pathlib import Path
from tests.evaluate_heldout import pipeline_fingerprint

ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'evaluation'
read=lambda name:json.loads((HERE/name).read_text(encoding='utf-8'))
before=[read('heldout_retest_v9.json')]+[read(f'fresh_v{i}_retest_v9.json') for i in range(2,9)]+[read('fresh_results_v9.json')]
current=[read('heldout_retest_v10.json')]+[read(f'fresh_v{i}_retest_v10.json') for i in range(2,10)]
fresh=read('fresh_results_v10.json')
pipeline,_=pipeline_fingerprint()
for r in current+[fresh]:
    assert r['pipeline_sha256_before']==r['pipeline_sha256_after']==pipeline
    assert r['parser_unchanged'] and not any(c['exception'] for c in r['cases'])
for a,b in zip(before,current):
    assert a['dataset_sha256']==b['dataset_sha256']
    assert [(c['id'],c['text'],c['expected_actions']) for c in a['cases']]==[(c['id'],c['text'],c['expected_actions']) for c in b['cases']]
    assert not any(x['exact_match'] and not y['exact_match'] for x,y in zip(a['cases'],b['cases']))
assert fresh['matches_frozen_parser']
assert hashlib.sha256((ROOT/'tests/fresh_commands_v10.json').read_bytes()).hexdigest()==fresh['dataset_sha256']
assert {b['id'] for a,b in zip(before[-1]['cases'],current[-1]['cases']) if not a['exact_match'] and b['exact_match']}=={'P42','P47','P49','P50'}
assert sum(not c['expected_actions'] for c in fresh['cases'] if c['scope']=='core')==11


def score(r,k='exact_match'):
    m=r['metrics'][k]
    accuracy=f"{m['accuracy']:.1%}" if m['accuracy'] is not None else 'N/A'
    return f"{m['correct']}/{m['total']} ({accuracy})"


lines=[
 '# WordWorld quarter, of-each-color, mixed-location and future-perfect fixes — 15 October 2026','',
 '**Nine saved-set retests: '+', '.join(score(r) for r in current)+'. Tenth fresh set: '+score(fresh)+'.**','',
 'All four targeted ninth-set errors pass: P42 (quarters), P49 (of each color), P50 (mixed shared placement) and P47 (future perfect). The ninth set improves from 40/50 to 44/50. No previously passing exact match regressed across the nine saved sets. Historical labels and first-run predictions are unchanged.','',
 '## Changes','',
 '- Quarter groups reuse fraction partitions with explicit numerator/denominator arithmetic. Supports a/one/two/three quarters, digits, hyphenated forms, of them, mapped part colors, mixed halves/quarters and inferred rest. A declared total must yield whole non-negative object counts, and group sums must agree with it. Missing totals, nonintegral groups, invalid numerators and inconsistent partitions abstain. Arithmetic precedes the existing 16-per-action cap.',
 '- Adjacent `of each color/colour` lists expand one explicit noun count across distinct supported colors. Lists can use a colon or comma and remain scoped to that noun. Missing/invalid counts, unsupported/duplicate colors and contradictory source colors abstain. Counts, spans, references, limits and mixed follow-on nouns use the existing action schema.',
 '- Shared `, all <location>` tails resolve once before source objects enter request-local reference state. Every source group in the same creation clause receives that placement, including mixed types and quarter/each groups. A new explicit verb begins another clause. Missing/chained/negated/conflicting locations and spatially filtered removal abstain. Pronoun landmark bindings continue pointing to the prior introductions.',
 '- Mapped roof/foliage/petal clauses accept will/shall have been painted/colored/coloured with bounded passive adverbs. Negation and unmapped parts abstain. Whole-object future-perfect clauses without an explicit mapped part remain unsupported.',
 '- Fixed a reporting-only evaluator error: empty spatial/settings subsets display N/A instead of formatting None as a percentage. The tenth sample has zero settings cases. Its original CLI printed the main scores and failed after saving all first-run predictions; a retry to a separate ignored output matched that preserved JSON exactly. No backend or gold changes followed the fresh run.','',
 '## Verification','',
 '| Check | Result |','|---|---|',
 '| Python parser/API/evaluator suite | 525 passed; 58 grammar cases and one evaluator regression added |',
 '| Original development commands | 50/50 exact actions |',
 '| Scene/preview unit tests | 16 passed |',
 '| Desktop/mobile browser suite | 44 passed locally |',
 '| React production build | Passed |','',
 'The added browser flow verifies visible blue/white quarter foliage, red/white each-color groups, common anchor IDs for mixed houses/flowers near the lake, a purple future-perfect roof, source highlights and undo/redo. Existing five-width mobile/tablet/landscape checks remain green. Screenshots: `.runtime/quarter-fixes-desktop.png` and `.runtime/quarter-fixes-mobile.png`.','',
 '## Evaluation method','',
 'The tenth sample freezes all 50 strings, expected action dictionaries, 40 core/10 broader-probe scopes and backend fingerprints before first prediction. Normalized exact-overlap checks include all ten earlier datasets, Python test literals, browser smoke/responsive/capture and UI example literals, README/archive lines and decoded example links. Similar grammar is intentional; semantic independence is not claimed.',
 '',
 'The author saw the implementation and earlier errors. These are implementation-aware hand-authored diagnostics, not independent human-labeled or random real-user accuracy estimates. No parser rules or gold labels were tuned after tenth-set predictions. The evaluator console-only fix did not change predictions or backend fingerprints. Different fresh samples are not paired before/after measurements.',
 '',
 '**Fresh: 40/50 (80%), with 40/40 core and 0/10 broader probes.** Eleven core commands expect no actions for zero/invalid/negated forms; 29 expect actual actions. No settings-bearing commands were included, so fresh settings accuracy is N/A, not 0%. Geometry and cross-request conversations are not scored.','',
 '| Set | Previous round | Current round |','|---|---:|---:|',
]
for i,(a,b) in enumerate(zip(before,current),1):
    lines.append(f'| Saved diagnostic set {i} | {score(a)} | {score(b)} |')
lines += [f'| Tenth fresh 50 | First execution | {score(fresh)} |','',
 '| Per-command metric | Set 1 | Set 2 | Set 3 | Set 4 | Set 5 | Set 6 | Set 7 | Set 8 | Set 9 | Fresh 10 |','|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
for key,label in [('intent','Intent sequence'),('entity_count_color','Objects/counts/colors'),('spatial','Spatial, gold-spatial subset'),('settings','Settings, gold-setting subset')]:
    lines.append('| '+label+' | '+' | '.join(score(r,key) for r in current+[fresh])+' |')
lines += ['',
 'Exact match compares every field of every ordered action dictionary. Field metrics compare per-command sequences, not tokens. Object metrics include empty typed-action lists; spatial/settings metrics use gold-bearing subsets.','',
 '## Main remaining errors','',
 'All ten broader tenth-set probes fail; no parser exceptions occurred. Q42, Q47 and Q49 silently create default-colored objects instead of the requested distribution. The nine saved sets retain 35 errors, fully detailed below.','',
 '| Pattern | Case | Actual behavior |','|---|---|---|',
 '| Total inside part phrase | Q41 | `with a total of seven roofs` abstains. |',
 '| Thirds | Q42 | Adds twelve default-colored trees, without notice. |',
 '| Semicolon remainder | Q43 | Ends partition scope and refuses. |',
 '| Former reference | Q44 | Omits the additional group, with notice. |',
 '| Multiplicative groups | Q45 | `three clusters of four` abstains. |',
 '| Subordinate creation | Q46 | Preservation swallows `while building`, with notice. |',
 '| Percentage distribution | Q47 | Adds eight default-colored flowers, without notice. |',
 '| Trailing each count | Q48 | `three of each` after the color list abstains. |',
 '| Alternate each word order | Q49 | `in each of blue and green` produces two default-color houses, without notice. |',
 '| Whole-object future perfect | Q50 | `a cottage that will have been painted blue` abstains without an explicit roof. |','',
 'Prioritize silent incorrect distribution (thirds, percentages and alternate each wording), then collection references and scope across clauses. Full predictions distinguish refusal, partial execution and incorrect actions.','',
 '## All 50 fresh commands','', '| ID | Scope | Result | Command |','|---|---|---|---|',
]
for c in fresh['cases']:
    lines.append(f"| {c['id']} | {c['scope']} | {'PASS' if c['exact_match'] else 'FAIL'} | {c['text']} |")
for title,r in [('Tenth-set failures',fresh)]+[(f'Saved set {i} failures',r) for i,r in enumerate(current,1) if any(not c['exact_match'] for c in r['cases'])]:
    lines += ['',f'## {title}','']
    for c in r['cases']:
        if c['exact_match']: continue
        lines += [f"### {c['id']}: {c['text']}",'','Expected:','','```json',json.dumps(c['expected_actions'],indent=2,ensure_ascii=False),'```','','Actual:','','```json',json.dumps(c['predicted_actions'],indent=2,ensure_ascii=False),'```','','Notices: '+('; '.join(c['warnings']) or 'None.'),'']
lines += ['## Reproduce','','Use new output names for future retests to preserve historical evidence. From the root:','','```powershell',
 '.\\.venv\\Scripts\\python.exe -m pytest -q tests',
 '.\\.venv\\Scripts\\python.exe -m tests.evaluate']
for i,r in enumerate(current+[fresh],1):
    dataset='tests/heldout_commands.json' if i==1 else f'tests/fresh_commands_v{i}.json'
    output='evaluation/heldout_retest_v10.json' if i==1 else f'evaluation/fresh_v{i}_retest_v10.json' if i<10 else 'evaluation/fresh_results_v10.json'
    lines.append(f'.\\.venv\\Scripts\\python.exe -X utf8 -m tests.evaluate_heldout --dataset {dataset} --dataset-sha256 {r["dataset_sha256"]} '+('--allow-parser-change ' if i<10 else '')+f'--output {output}')
lines += ['.\\.venv\\Scripts\\python.exe -X utf8 -m evaluation.write_quarter_report','```','',
 'From `frontend/`: `npm test`, `npm run build`, `npm run test:e2e` with both servers running. Set `WORDWORLD_BASE_URL` for production checks.','',
 'Gold: `tests/fresh_commands_v10.json`. First predictions: `evaluation/fresh_results_v10.json`. Regressions: `tests/test_quarter_fixes.py`, `tests/test_evaluation_empty_metrics.py`, `frontend/tests/browser/smoke.spec.js`.','',
 f"Parser SHA256: `{fresh['parser_sha256_before']}`.",
 f"Backend pipeline SHA256: `{pipeline}`.",
 f"Tenth dataset SHA256: `{fresh['dataset_sha256']}`.",'',
 'All ten evaluations verified the same backend fingerprint before and after prediction. Original labels/results were preserved.','']
out=HERE/'quarter_fixes_report.md'
out.write_text('\n'.join(lines),encoding='utf-8')
print(out)
