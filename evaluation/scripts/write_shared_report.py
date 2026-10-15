"""Record ninth-round labels, saved-set retests, errors and mobile verification."""
import hashlib
import json
from pathlib import Path
from tests.evaluate_heldout import pipeline_fingerprint

ROOT=Path(__file__).resolve().parents[2]
HERE=ROOT/'evaluation'/'results'
REPORTS=ROOT/'evaluation'/'reports'
read=lambda name:json.loads((HERE/name).read_text(encoding='utf-8'))
before=[read('heldout_retest_v8.json')]+[read(f'fresh_v{i}_retest_v8.json') for i in range(2,8)]+[read('fresh_results_v8.json')]
current=[read('heldout_retest_v9.json')]+[read(f'fresh_v{i}_retest_v9.json') for i in range(2,9)]
fresh=read('fresh_results_v9.json')
pipeline,_=pipeline_fingerprint()
for r in current+[fresh]:
    assert r['pipeline_sha256_before']==r['pipeline_sha256_after']==pipeline
    assert r['parser_unchanged']
for a,b in zip(before,current):
    assert a['dataset_sha256']==b['dataset_sha256']
    assert [(c['id'],c['text'],c['expected_actions']) for c in a['cases']]==[(c['id'],c['text'],c['expected_actions']) for c in b['cases']]
    assert not any(x['exact_match'] and not y['exact_match'] for x,y in zip(a['cases'],b['cases']))
assert fresh['matches_frozen_parser']
assert hashlib.sha256((ROOT/'tests/fresh_commands_v9.json').read_bytes()).hexdigest()==fresh['dataset_sha256']
assert {b['id'] for a,b in zip(before[-1]['cases'],current[-1]['cases']) if not a['exact_match'] and b['exact_match']}=={'N42','N43','N45','N49'}
assert sum(not c['expected_actions'] for c in fresh['cases'] if c['scope']=='core')==9


def score(r,k='exact_match'):
    m=r['metrics'][k]
    return f"{m['correct']}/{m['total']} ({m['accuracy']:.1%})"


lines=[
 '# WordWorld storm, half quantities, shared locations and future passive fixes — 15 October 2026','',
 '**Eight saved-set retests: '+', '.join(score(r) for r in current)+'. Ninth fresh set: '+score(fresh)+'.**','',
 'All four targeted eighth-set errors now pass: N49 (dawn and stop the storm), N42 (half-and-half), N43 (shared comma location) and N45 (future passive). L45 and M46 also improve. No previously passing exact match regressed across the eight saved sets. Historical labels and first-run predictions remain intact.','',
 '## Changes','',
 '- Stop/end weather phrases are matched before embedded rain/storm words. Negated controls leave weather unchanged and report a notice. Coordinated controls execute in order. Dawn maps to day, completing the observed mixed setting request.',
 '- Adjacent half groups require an explicit even whole-number total and a comma/colon partition. `half pink and half white` divides that total into integer groups. Supports `half of them`, shared colors, part clauses, placement, inferred rest and request-local references. Odd, missing, inconsistent or additive half totals abstain. Arithmetic precedes the existing 16-per-action cap.',
 '- A comma followed by `all` plus a supported location remains attached to the preceding same-noun counted collection. Every group receives the placement, with no extra landmark creation. Missing landmarks, negated constraints and conflicting placements retain refusal behavior. Shared tails across different source noun types remain unsupported.',
 '- Adjacent part clauses accept will/shall be painted/colored/coloured with supported passive adverbs. Negation, unmapped parts and ambiguous colors abstain. Future perfect remains outside this grammar.',
 '- Mobile: the single command editor moves above the island on phones and narrow landscape screens; drafts and scenes survive breakpoint changes. Create has a visible label, Enter inserts a newline on phones, textarea text is 16px, primary touch controls are at least 44 by 44 pixels, help remains available, and the help dialog scrolls within short screens. An explicit canvas width fixes tablet overflow. See [mobile QA](../docs/MOBILE_QA.md) for screenshots and limits.','',
 '## Verification','',
 '| Check | Result |','|---|---|',
 '| Python parser/API suite | 466 passed; 44 added regressions |',
 '| Original development commands | 50/50 exact actions |',
 '| Scene/preview unit tests | 16 passed |',
 '| Desktop/mobile browser suite | 42 passed locally |',
 '| React production build | Passed |','',
 'The browser suite covers storm clearing, half/future/shared-location actions, actual colors, placement guides, source highlights and saved geometry. Added responsive checks cover 320x740, 390x844, 430x932, 768x1024 and 844x390 in desktop and mobile Chromium contexts, plus desktop/phone switching, draft preservation, mobile newlines and help-dialog alignment. Desktop behavior and existing editing/undo/error tests remain green.','',
 '## Evaluation method','',
 'The ninth sample freezes all 50 strings, gold actions, 40 core/10 broader-probe scopes and backend fingerprints before first prediction. Normalized exact-overlap checks include all nine earlier datasets, Python regression literals, browser smoke/responsive/capture and UI example literals, README/archive lines and decoded example links. Similar grammar is intentional; semantic independence is not claimed.',
 '',
 'The author saw the implementation and earlier failures. These are implementation-aware hand-authored diagnostics, not independent human-labeled or random real-user accuracy estimates. No parser rules or gold labels were changed after ninth-set predictions. Different fresh samples are not paired before/after measurements.',
 '',
 '**Fresh: 40/50 (80%), with 40/40 core and 0/10 broader probes.** Nine core commands expect no actions for invalid/zero/negated inputs; the other 31 expect actual actions. Parser scores do not measure sprite size, placement geometry or cross-request conversation.','',
 '| Set | Previous round | Current round |','|---|---:|---:|',
]
for i,(a,b) in enumerate(zip(before,current),1):
    lines.append(f'| Saved diagnostic set {i} | {score(a)} | {score(b)} |')
lines += [f'| Ninth fresh 50 | First execution | {score(fresh)} |','',
 '| Per-command metric | Set 1 | Set 2 | Set 3 | Set 4 | Set 5 | Set 6 | Set 7 | Set 8 | Fresh 9 |','|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
for key,label in [('intent','Intent sequence'),('entity_count_color','Objects/counts/colors'),('spatial','Spatial, gold-spatial subset'),('settings','Settings, gold-setting subset')]:
    lines.append('| '+label+' | '+' | '.join(score(r,key) for r in current+[fresh])+' |')
lines += ['',
 'Exact match compares every field of every ordered action dictionary. Field metrics compare per-command sequences, not tokens. Object metrics include empty typed-action lists; spatial/settings metrics use gold-bearing subsets.','',
 '## Main remaining errors','',
 'All ten broader ninth-set probes fail; no parser exceptions occurred. P42 and P49 silently emit default-colored objects instead of the requested distribution. The eight saved sets retain 29 errors, fully detailed below.','',
 '| Pattern | Case | Actual behavior |','|---|---|---|',
 '| Total inside a part phrase | P41 | `with a total of eight roofs` abstains. |',
 '| Quarter distribution | P42 | Creates eight default-colored trees, without notice. |',
 '| Semicolon remainder | P43 | Ends collection scope and refuses. |',
 '| Latter reference | P44 | Omits the extra group, with notice. |',
 '| Multiplicative groups | P45 | `four bunches of three` abstains. |',
 '| Subordinate creation | P46 | Preservation swallows `while planting`, with notice. |',
 '| Future perfect | P47 | `will have been painted` abstains. |',
 '| Others remainder | P48 | `the others` is unsupported; total mismatch refuses. |',
 '| Each word order | P49 | `three flowers of each color` produces three default-colored flowers, without notice. |',
 '| Mixed-type shared location | P50 | Creates both types but drops placement, with notice. |','',
 'Prioritize silent incorrect execution (P42/P49), then modifier scope across object types and collection references. Do not interpret notices as proof that unsupported requests caused no scene changes; partial actions are shown below.','',
 '## All 50 fresh commands','', '| ID | Scope | Result | Command |','|---|---|---|---|',
]
for c in fresh['cases']:
    lines.append(f"| {c['id']} | {c['scope']} | {'PASS' if c['exact_match'] else 'FAIL'} | {c['text']} |")
for title,r in [('Ninth-set failures',fresh)]+[(f'Saved set {i} failures',r) for i,r in enumerate(current,1) if any(not c['exact_match'] for c in r['cases'])]:
    lines += ['',f'## {title}','']
    for c in r['cases']:
        if c['exact_match']: continue
        lines += [f"### {c['id']}: {c['text']}",'','Expected:','','```json',json.dumps(c['expected_actions'],indent=2,ensure_ascii=False),'```','','Actual:','','```json',json.dumps(c['predicted_actions'],indent=2,ensure_ascii=False),'```','','Notices: '+('; '.join(c['warnings']) or 'None.'),'']
lines += ['## Reproduce','','Use new output names for future retests to preserve historical evidence. From the root:','','```powershell',
 '.\\.venv\\Scripts\\python.exe -m pytest -q tests',
 '.\\.venv\\Scripts\\python.exe -m tests.evaluate']
for i,r in enumerate(current+[fresh],1):
    dataset='tests/heldout_commands.json' if i==1 else f'tests/fresh_commands_v{i}.json'
    output='evaluation/results/heldout_retest_v9.json' if i==1 else f'evaluation/fresh_v{i}_retest_v9.json' if i<9 else 'evaluation/results/fresh_results_v9.json'
    lines.append(f'.\\.venv\\Scripts\\python.exe -X utf8 -m tests.evaluate_heldout --dataset {dataset} --dataset-sha256 {r["dataset_sha256"]} '+('--allow-parser-change ' if i<9 else '')+f'--output {output}')
lines += ['.\\.venv\\Scripts\\python.exe -X utf8 -m evaluation.scripts.write_shared_report','```','',
 'From `frontend/`: `npm test`, `npm run build`, `npm run test:e2e` with both servers running. Set `WORDWORLD_BASE_URL` to test production.','',
 'Gold: `tests/fresh_commands_v9.json`. Predictions/notices: `evaluation/results/fresh_results_v9.json`. Regressions: `tests/test_shared_fixes.py`, `frontend/tests/browser/mobile.spec.js`, `frontend/tests/browser/smoke.spec.js`.','',
 f"Parser SHA256: `{fresh['parser_sha256_before']}`.",
 f"Backend pipeline SHA256: `{pipeline}`.",
 f"Ninth dataset SHA256: `{fresh['dataset_sha256']}`.",'',
 'All nine evaluations verified the same backend fingerprint before and after prediction. No subsequent backend or gold tuning occurred.','']
out=REPORTS/'shared_fixes_report.md'
out.write_text('\n'.join(lines),encoding='utf-8')
print(out)
