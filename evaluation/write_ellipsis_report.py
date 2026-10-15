"""Record quantity/roof/ellipsis fixes and all five versioned evaluations."""
import hashlib
import json
from pathlib import Path

from tests.evaluate_heldout import pipeline_fingerprint

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
read = lambda name: json.loads((HERE/name).read_text(encoding='utf-8'))
before = [read(n) for n in ['heldout_retest_v4.json','fresh_v2_retest_v4.json','fresh_v3_retest_v4.json','fresh_results_v4.json']]
current = [read(n) for n in ['heldout_retest_v5.json','fresh_v2_retest_v5.json','fresh_v3_retest_v5.json','fresh_v4_retest_v5.json']]
fresh = read('fresh_results_v5.json')
pipeline, _ = pipeline_fingerprint()
for report in current + [fresh]:
    assert report['pipeline_sha256_before'] == report['pipeline_sha256_after'] == pipeline
    assert report['parser_unchanged']
for old, report in zip(before,current):
    assert old['dataset_sha256'] == report['dataset_sha256']
    assert [(c['id'],c['text'],c['expected_actions']) for c in old['cases']] == [(c['id'],c['text'],c['expected_actions']) for c in report['cases']]
    assert not any(a['exact_match'] and not b['exact_match'] for a,b in zip(old['cases'],report['cases']))
assert fresh['matches_frozen_parser']
assert hashlib.sha256((ROOT/'tests/fresh_commands_v5.json').read_bytes()).hexdigest() == fresh['dataset_sha256']
improved = [b['id'] for a,b in zip(before[-1]['cases'],current[-1]['cases']) if not a['exact_match'] and b['exact_match']]
assert set(improved) == {'H41','H42','H43','H44','H46','H47'}


def score(report, key='exact_match'):
    m = report['metrics'][key]
    return f"{m['correct']}/{m['total']} ({m['accuracy']:.1%})"


lines = [
    '# WordWorld quantity, roof-clause and ellipsis fixes — 15 October 2026', '',
    f"**Four saved-set retests: {', '.join(score(r) for r in current)}. Fifth fresh set: {score(fresh)}.**", '',
    'All six targeted errors from the fourth set now pass: H42/H47 (exactly five/five in all), H41/H43 (painted roofs/nested roof clauses), H44 (three large ones), H46 (coordinated relative clauses). There are no new exact-match regressions on the four saved sets. Historical labels and original predictions remain intact.', '',
    'The fifth set contains 50 newly hand-authored commands, gold actions and scopes frozen before first prediction with backend source hashes. No normalized exact overlaps were found against the five earlier datasets (the development set and four diagnostic sets), Python regression literals, browser test literals or README lines at freeze time. Similar grammar constructions are intentional. The author saw the implementation and earlier errors, so these are diagnostic samples, not independent human-labeled or random real-user benchmarks.', '',
    '## Implemented behavior', '',
    '- `exactly` works with explicit whole-number quantities and group quantifiers before nouns and in post-noun appositives. `in all` joins the supported `in total`, `altogether`, and `of them` endings. Counts are read before creation and discourse references. Negative/fractional/ambiguous counts abstain; the existing 16-per-action cap applies.',
    '- Roof-color clauses include `roofs painted blue`, `with a roof that/which is yellow`, `whose roof is painted red`, and `that/which has a blue roof`, with colored/coloured variants. The same bounded grammar maps leaves/foliage and petals onto their existing visible colors. Negated/conflicting colors and unsupported object-part mappings abstain.',
    '- Adjacent counted `one/ones` groups inherit the most recent explicit source noun in the same creation phrase: `two small houses and three large ones` yields separate counts two and three. Only noun type is inherited; omitted color retains the existing default. These create new objects, so they are not ID references to existing objects. Explicit new verbs and intervening placement constraints end this inheritance scope.',
    '- Counted relative continuations such as `two trees that are green and three that are yellow`, including comma lists and `whose roof` clauses, yield separate actions and colors. Their groups remain available to bounded removal and spatial `them` references. A trailing placement applies to the adjacent groups under the documented shared-placement grammar.',
    '- Highlights retain exact original offsets, including quantities/colors and inherited `ones` as an object span. Per-group zero counts and negation skip only that group. Numeric conjunctions and hyphenated cardinals remain intact. Unresolved inherited nouns produce notices; a following landmark must not become an unintended creation.', '',
    'Small/large/tall/short describe groups only; sprite sizes are not changed or scored. Action grounding is deterministic and rule based; spaCy supplies annotations. No backend rules or frozen labels were changed after observing fifth-set predictions.', '',
    '## Verification', '', '| Check | Result |', '|---|---|',
    '| Python parser/API tests | 280 passed; 57 added regression cases |',
    '| Original development 50 | 50/50 exact action matches |',
    '| Scene/preview unit tests | 16 passed |',
    '| Desktop/mobile Chromium checks | 20 passed |',
    '| React production build | Passed |',
    '| Live API through Vite | Exactly five flowers returns count 5 |', '',
    'The browser flow checks five actual added flowers, purple/blue roofs across an inherited-noun group, separate yellow/pink tree groups anchoring a flower between them, exact inline highlights, and removal of newly introduced house groups while preserving older houses. Existing manipulation, undo/redo, autosave, weather and offline-preview checks also pass. Screenshots: `.runtime/ellipsis-fixes-desktop.png` and `.runtime/ellipsis-fixes-mobile.png`.', '',
    'The long-running backend initially served the previous parser despite file changes. Restarting the WordWorld FastAPI process restored the current rules; it now watches only `backend/`, avoiding reloads from test/report/backup files. The failed browser run was diagnosed from live API predictions, then the full desktop/mobile suite was rerun successfully. Vite and FastAPI remain running.', '',
    '## Evaluations', '', '| Set | Previous round | Current round | Interpretation |', '|---|---:|---:|---|',
]
for i,(old,report) in enumerate(zip(before,current),1):
    lines.append(f'| Diagnostic set {i} | {score(old)} | {score(report)} | Same gold labels; development retest |')
lines += [f'| Fifth fresh set | Not previously executed | {score(fresh)} | Gold and code frozen before prediction |', '',
    '| Per-command metric | Set 1 | Set 2 | Set 3 | Set 4 | Fresh set 5 |', '|---|---:|---:|---:|---:|---:|']
for key,label in [('intent','Intent sequence'),('entity_count_color','Objects/counts/colors'),('spatial','Spatial fields, gold-spatial subset'),('settings','Settings, gold-setting subset')]:
    lines.append('| '+label+' | '+' | '.join(score(r,key) for r in current+[fresh])+' |')
lines += ['',
    'Fresh scopes: **40/40 core and 1/10 broader probes**. Core includes zero/negated count groups and one reset-reference refusal. Probes test broader intended English beyond adjacent-group grammar. Different distributions prevent interpreting the new fresh score as a paired improvement over an earlier sample.', '',
    'Exact match compares every field of every ordered action dictionary. Field metrics are per-command sequences, not token scores. The object metric includes matching empty typed-action lists for pure settings. Spatial/setting metrics use gold-bearing subsets; geometry, scene manipulation and cross-request context are outside parser accuracy.', '',
    '## Remaining errors and next priorities', '',
    'The fifth set has **9 errors and no exceptions**. Four failures (J41, J45, J48, J50) emit wrong or partial actions without notices. The extra default object in J41 is the highest-priority remaining creation error.', '',
    '| Pattern | Cases | Actual behavior |', '|---|---|---|',
    '| Counted partitions after a bare plural | J41 | `trees, two that are green and three that are yellow` adds an extra uncolored tree before the requested two groups: six trees instead of five, without notice. |',
    '| Passive roof clause | J43 | `whose roof has been painted red` abstains with a notice. |',
    '| Shorter quantity ending | J44 | `flowers, five total` creates one flower and reports an unsupported second clause. |',
    '| Predicate ellipsis | J45 | `and three yellow` loses the second group without notice. |',
    '| Partitioned roof groups | J46 | `two houses, one with a blue roof and one with a green roof` abstains instead of splitting the total into two colored houses. |',
    '| Cross-clause noun-type inheritance | J47 | `add three large ones behind the tower` loses the new group with notices; the tower is correctly not created. |',
    '| Group multiplication | J48 | `three groups of two` creates one castle instead of six, without notice. |',
    '| Subordinate creation | J49 | Preservation swallows `while adding two blue houses`; no houses are added. |',
    '| Setting paraphrase | J50 | `daylight` is missed; snow clearing works, without a notice for the missing time change. |', '',
    'J42 passes: `exactly five blue-roofed cottages` produces five blue houses. This verifies that wording, not general compound-adjective understanding.', '',
    'The four saved sets retain twelve errors: F35/F48/F50, G43–G47, and H45/H48/H49/H50. They cover daylight, construct, subordinate creation, finite relation/direction paraphrases, group multiplication and weather paraphrases. Full predictions and notices follow below.', '',
    '## All 50 new commands', '', '| ID | Scope | Result | Command |', '|---|---|---|---|',
]
for c in fresh['cases']:
    lines.append(f"| {c['id']} | {c['scope']} | {'PASS' if c['exact_match'] else 'FAIL'} | {c['text']} |")
for title, report in [('Fresh fifth-set failures',fresh)] + [(f'Saved set {i} remaining failures',r) for i,r in enumerate(current,1) if any(not c['exact_match'] for c in r['cases'])]:
    lines += ['', f'## {title}', '']
    for c in report['cases']:
        if c['exact_match']:
            continue
        lines += [f"### {c['id']}: {c['text']}", '']
        if c.get('label_note'):
            lines += ['Gold rationale: '+c['label_note'], '']
        lines += ['Expected:', '', '```json', json.dumps(c['expected_actions'],indent=2,ensure_ascii=False), '```', '',
            'Actual:', '', '```json', json.dumps(c['predicted_actions'],indent=2,ensure_ascii=False), '```', '',
            'Notices: '+('; '.join(c['warnings']) or 'None.'), '']
lines += ['## Reproduce', '', 'From the project root:', '', '```powershell',
    '.\\.venv\\Scripts\\python.exe -m pytest -q tests',
    '.\\.venv\\Scripts\\python.exe -m tests.evaluate',
    '.\\.venv\\Scripts\\python.exe -X utf8 -m tests.evaluate_heldout --allow-parser-change --output evaluation/heldout_retest_v5.json']
for i, report in list(enumerate(current,1))[1:] + [(5,fresh)]:
    output = f'evaluation/fresh_v{i}_retest_v5.json' if i < 5 else 'evaluation/fresh_results_v5.json'
    lines.append(f'.\\.venv\\Scripts\\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v{i}.json --dataset-sha256 {report["dataset_sha256"]} '+('--allow-parser-change ' if i < 5 else '')+f'--output {output}')
lines += ['.\\.venv\\Scripts\\python.exe -X utf8 -m evaluation.write_ellipsis_report', '```', '',
    'From `frontend/`, with FastAPI and Vite running: `npm test`, `npm run test:e2e`, `npm run build`.', '',
    'Frozen labels: `tests/fresh_commands_v5.json`. Predictions/notices/metrics: `evaluation/fresh_results_v5.json`. Regressions: `tests/test_ellipsis_fixes.py`, `frontend/tests/browser/smoke.spec.js`.', '',
    f"Parser SHA256: `{fresh['parser_sha256_before']}`.",
    f"Backend pipeline SHA256: `{pipeline}`.",
    f"Fifth dataset SHA256: `{fresh['dataset_sha256']}`.", '',
    'All five evaluations verified the same backend source fingerprint before and after prediction. Frozen input hashes and gold labels are preserved. After these new errors inform future development, reruns need separate comparison outputs and a newly frozen sample for another fresh-command claim.', '',
]
assert sum(not c['exact_match'] and not c['warnings'] for c in fresh['cases']) == 4
out = HERE/'ellipsis_fixes_report.md'
out.write_text('\n'.join(lines),encoding='utf-8')
print(out)
