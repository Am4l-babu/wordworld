"""Record round eight from immutable labels and separate saved-set retests."""
import hashlib
import json
from pathlib import Path
from tests.evaluate_heldout import pipeline_fingerprint

ROOT=Path(__file__).resolve().parents[2]
HERE=ROOT/'evaluation'/'results'
REPORTS=ROOT/'evaluation'/'reports'
read=lambda name:json.loads((HERE/name).read_text(encoding='utf-8'))
before=[read('heldout_retest_v7.json')]+[read(f'fresh_v{i}_retest_v7.json') for i in range(2,7)]+[read('fresh_results_v7.json')]
current=[read('heldout_retest_v8.json')]+[read(f'fresh_v{i}_retest_v8.json') for i in range(2,8)]
fresh=read('fresh_results_v8.json')
pipeline,_=pipeline_fingerprint()
for r in current+[fresh]:
    assert r['pipeline_sha256_before']==r['pipeline_sha256_after']==pipeline
    assert r['parser_unchanged']
for a,b in zip(before,current):
    assert a['dataset_sha256']==b['dataset_sha256']
    assert [(c['id'],c['text'],c['expected_actions']) for c in a['cases']]==[(c['id'],c['text'],c['expected_actions']) for c in b['cases']]
    assert not any(x['exact_match'] and not y['exact_match'] for x,y in zip(a['cases'],b['cases']))
assert fresh['matches_frozen_parser']
assert hashlib.sha256((ROOT/'tests/fresh_commands_v8.json').read_bytes()).hexdigest()==fresh['dataset_sha256']
assert {b['id'] for a,b in zip(before[-1]['cases'],current[-1]['cases']) if not a['exact_match'] and b['exact_match']}=={'M41','M43','M45','M50'}
assert sum(not c['expected_actions'] for c in fresh['cases'] if c['scope']=='core')==9


def score(r,k='exact_match'):
    m=r['metrics'][k]
    return f"{m['correct']}/{m['total']} ({m['accuracy']:.1%})"


lines=[
 '# WordWorld weather, distributive counts, inferred remainders and passive adverbs — 15 October 2026','',
 '**Seven saved-set retests: '+', '.join(score(r) for r in current)+'. Eighth fresh set: '+score(fresh)+'.**','',
 'All targeted seventh-set failures pass: M50 (daylight and turn off the rain), M43 (three each), M41 (the rest) and M45 (passive adverb). Seven previously failing commands improve across saved sets, with no previously passing exact match regressing. Historical labels and first-run predictions are preserved.','',
 '## Changes','',
 '- Weather switches read `turn/switch on/off the rain/snow` and `turn/switch the rain/snow on/off` before weather keywords. Negated switches abstain instead of clearing/enabling weather. Coordinated switches preserve execution order. `daylight` maps to day, completing the previously observed mixed setting command.',
 '- One explicit count distributes across an adjacent list of two or more supported colors, before or after the object noun. `six flowers: three each of pink and white` creates two groups of three, with no default group. Commas inside the list stay in the noun phrase; counts, totals, negatives, zero groups, locations and references use the existing checks. Unknown/ambiguous colors and invalid/missing counts abstain. Highlights deduplicate shared number spans.',
 '- `the rest`, `the remainder` and `the remaining ones` infer total minus prior non-negated groups. A single final remainder and a declared total are required; negative, undefined, repeated, nonfinal or negated inferred remainders abstain. Arithmetic precedes per-action caps, references bind actual group actions, and a zero remainder adds nothing.',
 '- Bounded passive adverbs already/recently/just/newly/previously/freshly work around `been` and before present passive colors. Negation and unsupported modifiers such as almost still abstain. Colors continue mapping to house roofs, tree leaves/foliage and flower petals.',
 '- Deterministic grounding and the action schema are unchanged. spaCy remains responsible for linguistic annotations, not action extraction.','',
 '## Verification','',
 '| Check | Result |','|---|---|',
 '| Python parser/API suite | 422 passed; 62 added regressions |',
 '| Original development commands | 50/50 exact actions |',
 '| Scene/preview unit tests | 16 passed |',
 '| Desktop/mobile browser suite | 28 passed locally |',
 '| React production build | Passed |','',
 'The added browser flow turns rain on then off, checks pink/white distribution counts and stored colors, verifies inferred tree counts and actual SVG foliage colors, checks an orange passive-adverb roof, and exercises undo/redo. Screenshots are in `.runtime/distributive-fixes-desktop.png` and `.runtime/distributive-fixes-mobile.png`.','',
 '## Evaluation method','',
 'The eighth sample freezes all 50 commands, expected action dictionaries, 40 core/10 broader-probe scopes and backend fingerprints before first prediction. A normalized exact-overlap check covers all eight earlier datasets, Python test literals, browser smoke/capture and UI example literals, README/archive lines and decoded example links. Similar grammar is intentional; semantic independence is not claimed.',
 '',
 'The author saw the implementation and earlier failures. These are implementation-aware hand-authored diagnostics, not independent human-labeled or random real-user accuracy estimates. No parser rules or gold labels were changed after eighth-set predictions. Different fresh samples are not paired before/after measurements.',
 '',
 '**Fresh: 40/50 (80%), with 40/40 core and 0/10 broader probes.** Nine core commands deliberately expect no actions for invalid/zero/negated inputs. The other 31 core commands expect actual actions. This split limits the meaning of the 100% core score. Geometry, sprite size and cross-request references are not measured.','',
 '| Set | Previous round | Current round |','|---|---:|---:|',
]
for i,(a,b) in enumerate(zip(before,current),1):
    lines.append(f'| Saved diagnostic set {i} | {score(a)} | {score(b)} |')
lines += [f'| Eighth fresh 50 | First execution | {score(fresh)} |','',
 '| Per-command metric | Set 1 | Set 2 | Set 3 | Set 4 | Set 5 | Set 6 | Set 7 | Fresh 8 |','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
for key,label in [('intent','Intent sequence'),('entity_count_color','Objects/counts/colors'),('spatial','Spatial, gold-spatial subset'),('settings','Settings, gold-setting subset')]:
    lines.append('| '+label+' | '+' | '.join(score(r,key) for r in current+[fresh])+' |')
lines += ['',
 'Exact match compares every field of every ordered action dictionary. Field metrics compare per-command sequences, not tokens; the object metric includes empty typed-action lists. Spatial/settings metrics use gold-bearing subsets.','',
 '## Main remaining errors','',
 'All ten broader eighth-set probes fail; no parser exceptions occurred. N42 silently drops fractional color distribution. N49 incorrectly turns on rain for stop the storm and ignores dawn, although an unrelated pronoun notice appears. Prioritize incorrect execution before adding further paraphrases. The seven saved sets retain 25 failures, all detailed below.','',
 '| Pattern | Case | Actual behavior |','|---|---|---|',
 '| Total inside a part phrase | N41 | `with a total of six roofs` abstains. |',
 '| Half-and-half distribution | N42 | Adds eight default-colored flowers; no notice. |',
 '| Shared comma tail | N43 | Drops `all behind the tower`; groups are created without placement, with notice. |',
 '| Semicolon remainder | N44 | Ends partition scope and refuses instead of resolving the rest. |',
 '| Future passive | N45 | `will be painted` abstains. |',
 '| Former reference | N46 | Omits the requested additional group, with notice. |',
 '| Multiplicative groups | N47 | `four clusters of two` abstains. |',
 '| Subordinate creation | N48 | Preservation swallows `while drawing`, with notice. |',
 '| Weather/time paraphrases | N49 | Dawn is ignored and stop the storm enables rain; pronoun notice is unhelpful. |',
 '| Others remainder | N50 | `the others` is unsupported; partition-total mismatch refuses. |','',
 '## All 50 fresh commands','', '| ID | Scope | Result | Command |','|---|---|---|---|',
]
for c in fresh['cases']:
    lines.append(f"| {c['id']} | {c['scope']} | {'PASS' if c['exact_match'] else 'FAIL'} | {c['text']} |")
for title,r in [('Eighth-set failures',fresh)]+[(f'Saved set {i} failures',r) for i,r in enumerate(current,1) if any(not c['exact_match'] for c in r['cases'])]:
    lines += ['',f'## {title}','']
    for c in r['cases']:
        if c['exact_match']: continue
        lines += [f"### {c['id']}: {c['text']}",'','Expected:','','```json',json.dumps(c['expected_actions'],indent=2,ensure_ascii=False),'```','','Actual:','','```json',json.dumps(c['predicted_actions'],indent=2,ensure_ascii=False),'```','','Notices: '+('; '.join(c['warnings']) or 'None.'),'']
lines += ['## Reproduce','','Use separate output names for later retests; preserve historical predictions. From the root:','','```powershell',
 '.\\.venv\\Scripts\\python.exe -m pytest -q tests',
 '.\\.venv\\Scripts\\python.exe -m tests.evaluate']
for i,r in enumerate(current+[fresh],1):
    dataset='tests/heldout_commands.json' if i==1 else f'tests/fresh_commands_v{i}.json'
    output='evaluation/results/heldout_retest_v8.json' if i==1 else f'evaluation/fresh_v{i}_retest_v8.json' if i<8 else 'evaluation/results/fresh_results_v8.json'
    lines.append(f'.\\.venv\\Scripts\\python.exe -X utf8 -m tests.evaluate_heldout --dataset {dataset} --dataset-sha256 {r["dataset_sha256"]} '+('--allow-parser-change ' if i<8 else '')+f'--output {output}')
lines += ['.\\.venv\\Scripts\\python.exe -X utf8 -m evaluation.scripts.write_distributive_report','```','',
 'From `frontend/`: `npm test`, `npm run build`, `npm run test:e2e` with both servers running. Set `WORDWORLD_BASE_URL` for production browser verification.','',
 'Gold: `tests/fresh_commands_v8.json`. Predictions/notices: `evaluation/results/fresh_results_v8.json`. Regressions: `tests/test_distributive_fixes.py`, `frontend/tests/browser/smoke.spec.js`.','',
 f"Parser SHA256: `{fresh['parser_sha256_before']}`.",
 f"Backend pipeline SHA256: `{pipeline}`.",
 f"Eighth dataset SHA256: `{fresh['dataset_sha256']}`.",'',
 'All eight evaluations verified the same backend fingerprint before and after prediction. Frozen source hashes match the tested parser; no subsequent rule/gold tuning occurred.','']
out=REPORTS/'distributive_fixes_report.md'
out.write_text('\n'.join(lines),encoding='utf-8')
print(out)
