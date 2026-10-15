"""Write the seventh diagnostic round from preserved predictions and labels."""
import hashlib
import json
from pathlib import Path
from tests.evaluate_heldout import pipeline_fingerprint

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT/'evaluation'/'results'
REPORTS = ROOT/'evaluation'/'reports'
read = lambda n: json.loads((HERE/n).read_text(encoding='utf-8'))
before = [read('heldout_retest_v6.json')] + [read(f'fresh_v{i}_retest_v6.json') for i in range(2,6)] + [read('fresh_results_v6.json')]
current = [read('heldout_retest_v7.json')] + [read(f'fresh_v{i}_retest_v7.json') for i in range(2,7)]
fresh = read('fresh_results_v7.json')
pipeline, _ = pipeline_fingerprint()
for r in current+[fresh]:
    assert r['pipeline_sha256_before'] == r['pipeline_sha256_after'] == pipeline
    assert r['parser_unchanged']
for a,b in zip(before,current):
    assert a['dataset_sha256'] == b['dataset_sha256']
    assert [(c['id'],c['text'],c['expected_actions']) for c in a['cases']] == [(c['id'],c['text'],c['expected_actions']) for c in b['cases']]
    assert not any(x['exact_match'] and not y['exact_match'] for x,y in zip(a['cases'],b['cases']))
assert fresh['matches_frozen_parser']
assert hashlib.sha256((ROOT/'tests/fresh_commands_v7.json').read_bytes()).hexdigest() == fresh['dataset_sha256']
assert {b['id'] for a,b in zip(before[-1]['cases'],current[-1]['cases']) if not a['exact_match'] and b['exact_match']} == {'L41','L42','L43'}


def score(r,k='exact_match'):
    m=r['metrics'][k]
    return f"{m['correct']}/{m['total']} ({m['accuracy']:.1%})"


lines = [
 '# WordWorld colon, total-of and remainder fixes — 15 October 2026','',
 '**Six saved-set retests: '+', '.join(score(r) for r in current)+'. Seventh fresh set: '+score(fresh)+'.**','',
 'L41 (colon partition), L42 (a total of five) and L43 (the remaining three) now pass. Set six improves from 41/50 to 44/50; no previously passing case regressed on any of the six saved sets. Historical gold and predictions remain unchanged.','',
 '## Changes','',
 '- Colon-separated counted descriptions replace the noun default. Declared totals must equal the group sum, including one/ones groups. Shared source colors and original text offsets are retained.',
 '- Adjacent `a/the total of` quantities are anchored to the following number phrase, including exactly, pairs and dozen. Invalid, missing, negative, fractional, ambiguous or conflicting counts abstain. Existing per-action cap remains 16.',
 '- Explicitly counted `(the) remaining` groups require a declared total, must be unique and last, and must agree with total arithmetic. No implicit remainder is inferred for `the rest`. Successful groups participate in references without phantom default objects.',
 '- README command URLs safely prefill the editor without executing a request or resetting saved objects. The README includes a real animated recording, static poster, example links, native expandable guides and the existing Vercel full-stack preview.','',
 '## Verification','',
 '| Check | Result |','|---|---|',
 '| Python parser/API tests | 360 passed; 38 new regressions |',
 '| Original development set | 50/50 exact actions |',
 '| Scene/preview tests | 16 passed |',
 '| Local desktop/mobile Chromium | 26 passed |',
 '| React production build | Passed |','',
 'Browser checks verify colon groups, total-of counts, remainder highlights, actual scene colors/counts, safe URL input, markup isolation and oversized-query refusal. Existing editing, undo, references, API errors and mobile checks remain green. README captures come from the full local spaCy-backed API; the GIF is five actual scene states, not an illustration of unimplemented behavior.','',
 '## Evaluation method','',
 'All 50 new command strings, expected action dictionaries and 40 core/10 capability-probe scopes were frozen before the first parser call. Backend and development-input SHA256 fingerprints are embedded in the dataset. A normalized exact-overlap check included all seven earlier datasets, Python test literals, browser smoke/capture literals, README/archive lines and decoded example URLs. Similar grammar is intentional; semantic independence is not claimed.',
 '',
 'The author saw the implementation and earlier failures. These are hand-authored diagnostic samples, not independent human-labeled or random real-user accuracy estimates. No backend rules or gold labels were changed after seventh-set predictions. Once these examples inform future changes, treat them as regressions and freeze another new sample.',
 '',
 '**Fresh split: 40/40 core and 0/10 broader probes. Overall: 40/50 (80%).** Ten core cases expect no action for zero, invalid, ambiguous or inconsistent counts. Other cases mix valid groups with zero/negated groups. The core score must be read in that context. Different fresh samples are not paired before/after measurements.','',
 '| Set | Before this round | Current round |','|---|---:|---:|',
]
for i,(a,b) in enumerate(zip(before,current),1):
    lines.append(f'| Saved diagnostic set {i} | {score(a)} | {score(b)} |')
lines += [f'| Seventh fresh 50 | Not previously executed | {score(fresh)} |','',
 '| Per-command metric | Set 1 | Set 2 | Set 3 | Set 4 | Set 5 | Set 6 | Fresh 7 |','|---|---:|---:|---:|---:|---:|---:|---:|']
for key,label in [('intent','Intent sequence'),('entity_count_color','Objects/counts/colors'),('spatial','Spatial, gold-spatial subset'),('settings','Settings, gold-setting subset')]:
    lines.append('| '+label+' | '+' | '.join(score(r,key) for r in current+[fresh])+' |')
lines += ['',
 'Exact match compares every field of every ordered action dictionary. Field metrics compare per-command sequences, not tokens. The object metric includes empty typed-action lists for settings-only cases; spatial and setting metrics use gold-bearing subsets. Parser scores do not measure placement geometry.','',
 '## Main remaining NLP errors','',
 'All ten broader seventh-set probes fail; no parser exceptions occurred. Two silently emit wrong actions without notices (M43 and M50). The six saved sets retain 22 failures in total.','',
 '| Pattern | Case | Actual behavior |','|---|---|---|',
 '| Implicit remainder | M41 | `the rest green` is not counted; refuses the inconsistent partition. |',
 '| Total inside a part phrase | M42 | `with a total of five roofs` abstains. |',
 '| Distributive quantity | M43 | `three each of pink and white` emits six default-colored flowers, without notice. |',
 '| Semicolon continuation | M44 | Semicolon ends the group scope; refuses instead of linking the remainder. |',
 '| Adverb in a passive clause | M45 | `has recently been coloured` abstains. |',
 '| Shared tail after a comma | M46 | Creates the right groups but drops `all beside the river`, with notice. |',
 '| Latter reference | M47 | Creates the first groups, omits the additional latter object, with notice. |',
 '| Multiplicative groups | M48 | `three rows of two` abstains rather than multiplying. |',
 '| Subordinate creation | M49 | Preservation swallows `while planting...`, with notice. |',
 '| Negated setting paraphrase | M50 | `turn off the rain` incorrectly enables rain; daylight is ignored; no notice. |','',
 'Prioritize M50 and M43 because their wrong actions are silent, followed by shared modifier scope and implicit remainders. Full predictions and notices below separate refusal from partial or incorrect execution.','',
 '## All 50 fresh commands','', '| ID | Scope | Result | Command |','|---|---|---|---|',
]
for c in fresh['cases']:
    lines.append(f"| {c['id']} | {c['scope']} | {'PASS' if c['exact_match'] else 'FAIL'} | {c['text']} |")
for title,r in [('Seventh-set failures',fresh)] + [(f'Saved set {i} failures',r) for i,r in enumerate(current,1) if any(not c['exact_match'] for c in r['cases'])]:
    lines += ['',f'## {title}','']
    for c in r['cases']:
        if c['exact_match']: continue
        lines += [f"### {c['id']}: {c['text']}",'','Expected:','','```json',json.dumps(c['expected_actions'],indent=2,ensure_ascii=False),'```','','Actual:','','```json',json.dumps(c['predicted_actions'],indent=2,ensure_ascii=False),'```','','Notices: '+('; '.join(c['warnings']) or 'None.'),'']
lines += ['## Reproduce','','From the root (use new output names to preserve historical evidence):','','```powershell',
 '.\\.venv\\Scripts\\python.exe -m pytest -q tests',
 '.\\.venv\\Scripts\\python.exe -m tests.evaluate']
for i,r in enumerate(current+[fresh],1):
    dataset='tests/heldout_commands.json' if i==1 else f'tests/fresh_commands_v{i}.json'
    output='evaluation/results/heldout_retest_v7.json' if i==1 else f'evaluation/fresh_v{i}_retest_v7.json' if i<7 else 'evaluation/results/fresh_results_v7.json'
    lines.append(f'.\\.venv\\Scripts\\python.exe -X utf8 -m tests.evaluate_heldout --dataset {dataset} --dataset-sha256 {r["dataset_sha256"]} '+('--allow-parser-change ' if i<7 else '')+f'--output {output}')
lines += ['.\\.venv\\Scripts\\python.exe -X utf8 -m evaluation.scripts.write_colon_report','```','',
 'From `frontend/`: `npm test`, `npm run test:e2e` (servers running), `npm run build`.','',
 'Frozen labels: `tests/fresh_commands_v7.json`. Predictions/notices: `evaluation/results/fresh_results_v7.json`. New regressions: `tests/test_colon_fixes.py`.','',
 f"Parser SHA256: `{fresh['parser_sha256_before']}`.",
 f"Backend pipeline SHA256: `{pipeline}`.",
 f"Seventh dataset SHA256: `{fresh['dataset_sha256']}`.",'',
 'All seven evaluations verified the same backend fingerprint before and after prediction. Original labels/results have not been overwritten.','']
assert sum(not c['exact_match'] and not c['warnings'] for c in fresh['cases']) == 2
out=REPORTS/'colon_fixes_report.md'
out.write_text('\n'.join(lines),encoding='utf-8')
print(out)
