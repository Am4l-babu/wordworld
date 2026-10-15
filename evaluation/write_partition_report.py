"""Record partition/passive/quantity/predicate fixes with frozen round six."""
import hashlib
import json
from pathlib import Path
from tests.evaluate_heldout import pipeline_fingerprint

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT/'evaluation'
read = lambda n: json.loads((HERE/n).read_text(encoding='utf-8'))
before = [read('heldout_retest_v5.json')] + [read(f'fresh_v{i}_retest_v5.json') for i in range(2,5)] + [read('fresh_results_v5.json')]
current = [read('heldout_retest_v6.json')] + [read(f'fresh_v{i}_retest_v6.json') for i in range(2,6)]
fresh = read('fresh_results_v6.json')
pipeline, _ = pipeline_fingerprint()
for r in current+[fresh]:
    assert r['pipeline_sha256_before'] == r['pipeline_sha256_after'] == pipeline
    assert r['parser_unchanged']
for a,b in zip(before,current):
    assert a['dataset_sha256'] == b['dataset_sha256']
    assert [(c['id'],c['text'],c['expected_actions']) for c in a['cases']] == [(c['id'],c['text'],c['expected_actions']) for c in b['cases']]
    assert not any(x['exact_match'] and not y['exact_match'] for x,y in zip(a['cases'],b['cases']))
assert fresh['matches_frozen_parser']
assert hashlib.sha256((ROOT/'tests/fresh_commands_v6.json').read_bytes()).hexdigest() == fresh['dataset_sha256']
assert {b['id'] for a,b in zip(before[-1]['cases'],current[-1]['cases']) if not a['exact_match'] and b['exact_match']} == {'J41','J43','J44','J45','J46'}


def score(r,k='exact_match'):
    m=r['metrics'][k]
    return f"{m['correct']}/{m['total']} ({m['accuracy']:.1%})"


lines = [
 '# WordWorld counted partitions and attribute fixes — 15 October 2026','',
 '**Five saved-set retests: '+', '.join(score(r) for r in current)+'. Sixth fresh set: '+score(fresh)+'.**','',
 'J41 (extra default tree), J46 (partitioned roof groups), J43 (passive roof clause), J44 (five total) and J45 (omitted predicate) now pass. No previously passing exact-match cases regressed on the five saved sets. Historical labels and prediction files were preserved.','',
 '## Changes','',
 '- Comma-separated counted descriptions supply the collection instead of adding a bare noun default first. `trees, two green and three yellow` produces exactly five trees in two groups. Collective alias defaults are also replaced by explicit descriptions.',
 '- When a declared total is followed by relative/part/color descriptions, group counts must sum to it. `two houses, one with a blue roof and one with a green roof` creates two houses; a conflicting total abstains with a notice. Count agreement also disambiguates appositive one/ones groups. Existing explicitly additive and-groups and nonmatching appositive ones additions retain their documented behavior.',
 '- Count-first continuation reading handles one/ones, relative and part clauses, and omitted color predicates. `two trees that are green and three yellow` retains both groups. Explicit next nouns stay separate; quantities are never found by scanning through another noun or placement constraint.',
 '- Passive part clauses support has/have/had been painted/colored/coloured for mapped roofs, leaves/foliage and petals. `five total` joins existing post-noun quantity endings. Negated/conflicting attributes, mismatched totals and missing group quantities abstain with notices.',
 '- Shared source colors remain scoped to partitions. Per-group negation/zero counts, shared placement, exact source spans and reference bindings continue to work. Partition references bind only actual group actions, without a phantom default action. Rule-based grounding and the existing scene schema are unchanged.','',
 '## Verification','',
 '| Check | Result |','|---|---|',
 '| Python parser/API tests | 322 passed; 42 added cases |',
 '| Original development set | 50/50 exact actions |',
 '| Scene/preview tests | 16 passed |',
 '| Desktop/mobile Chromium | 22 passed |',
 '| React production build | Passed |','',
 'The new browser flow checks exactly five new green/yellow trees, two declared houses with distinct blue/purple roofs, five flowers from a trailing total, partition reference placement and undo/redo. Screenshots: `.runtime/partition-fixes-desktop.png` and `.runtime/partition-fixes-mobile.png`. Size descriptors still do not change sprite size; parser evaluation does not measure geometry.','',
 '## Evaluation method','',
 'The sixth sample has 50 new hand-authored commands, gold actions and scopes frozen before first prediction, with backend source and input hashes. There were no normalized exact overlaps with all six earlier datasets, Python regression literals, browser test literals or README lines at freeze time. Similar grammar is intentional. The author saw the implementation and previous failures; these are diagnostic samples, not independent human-labeled or random real-user accuracy estimates. No backend rules or labels were changed after observing sixth-set predictions.','',
 '**Fresh split: 40/40 core, 1/10 broader probes.** Core includes zero/negated groups and one zero-total refusal. Broader gold follows intended English outside the implemented syntax. The 82% overall score must be read with that split. Differing samples are not paired before/after comparisons.','',
 '| Set | Previous round | Current round |','|---|---:|---:|',
]
for i,(a,b) in enumerate(zip(before,current),1):
    lines.append(f'| Saved diagnostic set {i} | {score(a)} | {score(b)} |')
lines += [f'| Sixth fresh 50 | Not previously executed | {score(fresh)} |','',
 '| Per-command metric | Set 1 | Set 2 | Set 3 | Set 4 | Set 5 | Fresh 6 |','|---|---:|---:|---:|---:|---:|---:|']
for key,label in [('intent','Intent sequence'),('entity_count_color','Objects/counts/colors'),('spatial','Spatial fields, gold-spatial subset'),('settings','Settings, gold-setting subset')]:
    lines.append('| '+label+' | '+' | '.join(score(r,key) for r in current+[fresh])+' |')
lines += ['',
 'Exact match compares every field of every ordered action dictionary. Field metrics are per-command sequences, not token scores; the object metric includes matching empty typed-action lists in pure settings. Spatial/settings metrics use gold-bearing subsets.','',
 '## Remaining errors','',
 'The sixth set has nine errors and no exceptions. Three failures (L41, L42, L50) emit wrong or empty actions without notices.','',
 '| Pattern | Cases | Actual behavior |','|---|---|---|',
 '| Colon partitions | L41 | `five houses: two blue and three red` keeps only five default-color houses. |',
 '| Quantity word order | L42 | `a total of five` creates one flower instead of five, without notice. |',
 '| Remainder descriptions | L43 | `the remaining three` is missed, causing a total-mismatch refusal. |',
 '| Passive adverbs | L44 | `has already been painted` abstains. |',
 '| Shared tail after a comma | L45 | `all near the lake` is split off, dropping placement from otherwise correct groups. |',
 '| Latter references | L46 | `two more of the latter` loses the new group. |',
 '| Group multiplication | L47 | `two groups of three` abstains instead of creating six flowers. |',
 '| Subordinate creation | L48 | Preservation swallows `while building two houses`. |',
 '| Time/weather paraphrases | L50 | `daylight without any snow` emits no settings and no notice. |','',
 'L49 passes: `a bridge that goes over the stream` produces only a bridge across the river. This verifies that wording, not general finite-clause understanding. The saved sets retain sixteen errors, all listed below.','',
 '## All 50 fresh commands','', '| ID | Scope | Result | Command |','|---|---|---|---|',
]
for c in fresh['cases']:
    lines.append(f"| {c['id']} | {c['scope']} | {'PASS' if c['exact_match'] else 'FAIL'} | {c['text']} |")
for title,r in [('Sixth-set failures',fresh)] + [(f'Saved set {i} remaining failures',r) for i,r in enumerate(current,1) if any(not c['exact_match'] for c in r['cases'])]:
    lines += ['',f'## {title}','']
    for c in r['cases']:
        if c['exact_match']:
            continue
        lines += [f"### {c['id']}: {c['text']}",'','Expected:','','```json',json.dumps(c['expected_actions'],indent=2,ensure_ascii=False),'```','','Actual:','','```json',json.dumps(c['predicted_actions'],indent=2,ensure_ascii=False),'```','','Notices: '+('; '.join(c['warnings']) or 'None.'),'']
lines += ['## Reproduce','','From the root:','','```powershell',
 '.\\.venv\\Scripts\\python.exe -m pytest -q tests',
 '.\\.venv\\Scripts\\python.exe -m tests.evaluate',
 '.\\.venv\\Scripts\\python.exe -X utf8 -m tests.evaluate_heldout --allow-parser-change --output evaluation/heldout_retest_v6.json']
for i,r in list(enumerate(current,1))[1:]+[(6,fresh)]:
    output=f'evaluation/fresh_v{i}_retest_v6.json' if i<6 else 'evaluation/fresh_results_v6.json'
    lines.append(f'.\\.venv\\Scripts\\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v{i}.json --dataset-sha256 {r["dataset_sha256"]} '+('--allow-parser-change ' if i<6 else '')+f'--output {output}')
lines += ['.\\.venv\\Scripts\\python.exe -X utf8 -m evaluation.write_partition_report','```','',
 'From `frontend/`: `npm test`, `npm run test:e2e` (local servers running), `npm run build`.','',
 'Labels: `tests/fresh_commands_v6.json`. Predictions/notices: `evaluation/fresh_results_v6.json`. Regressions: `tests/test_partition_fixes.py`, `frontend/tests/browser/smoke.spec.js`.','',
 f"Parser SHA256: `{fresh['parser_sha256_before']}`.",
 f"Backend pipeline SHA256: `{pipeline}`.",
 f"Sixth dataset SHA256: `{fresh['dataset_sha256']}`.",'',
 'All six evaluations verified the same backend fingerprint before and after prediction. Once this sample informs future rule changes, use separate retest outputs and a new frozen sample for another fresh-command claim.','']
assert sum(not c['exact_match'] and not c['warnings'] for c in fresh['cases']) == 3
out=HERE/'partition_fixes_report.md'
out.write_text('\n'.join(lines),encoding='utf-8')
print(out)
