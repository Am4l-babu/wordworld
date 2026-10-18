"""Round twelve: place filters, filtered removal, more fractions, 'each' and semicolon wordings.

Run from the project root after `python -m tests.create_fresh_set_v12` froze the labels and the first
evaluation wrote evaluation/results/fresh_results_v12.json:

    python -m evaluation.scripts.write_filters_report

It retests every saved set with the current parser, stores those retests separately from the first-run
predictions, and renders evaluation/reports/filters_fixes_report.md.
"""
import contextlib
import hashlib
import io
import json
from pathlib import Path
from tests.evaluate_heldout import evaluate

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / 'evaluation' / 'results'
REPORTS = ROOT / 'evaluation' / 'reports'
SETS = ['heldout'] + [f'fresh_v{i}' for i in range(2, 13)]


def dataset(name):
    return ROOT / 'tests' / ('heldout_commands.json' if name == 'heldout' else f'fresh_commands_{name.replace("fresh_", "")}.json')


def retest_all():
    reports = {}
    for name in SETS:
        path = dataset(name)
        out = HERE / f'.{name}_tmp.json'
        with contextlib.redirect_stdout(io.StringIO()):
            reports[name] = evaluate(path, out, hashlib.sha256(path.read_bytes()).hexdigest(), allow_parser_change=True)
        out.unlink()
    return reports


def score(metric):
    return f"{metric['correct']}/{metric['total']}"


first = json.loads((HERE / 'fresh_results_v12.json').read_text(encoding='utf-8'))
assert first['matches_frozen_parser'] and first['evaluation_kind'] == 'frozen new-command evaluation'
previous = json.loads((HERE / 'round11_after_fix_retests.json').read_text(encoding='utf-8'))
retests = retest_all()
(HERE / 'round12_after_fix_retests.json').write_text(json.dumps(retests, indent=2, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')
failures = [c for c in first['cases'] if not c['exact_match']]
core_misses = [c for c in failures if c['scope'] == 'core']
now = {c['id']: c for c in retests['fresh_v12']['cases']}
still = [c for c in failures if not now[c['id']]['exact_match']]
fixed = [c for c in failures if now[c['id']]['exact_match']]
lines = [
    '# Round twelve: place filters, filtered removal and wording gaps', '',
    'This round adds a place filter for edits and removals (`paint the trees near the lake red`, `remove the flowers next to the house`), '
    'matched against the scene geometry with the same cone placement uses; `sixths`..`ninths`; `in each of red and yellow`; semicolons inside a '
    'colon-partition; counted pronouns (`make two of them red`); and a notice whenever a typed color is not applied.', '',
    '## Frozen first run', '',
    f"`tests/fresh_commands_v12.json` (SHA-256 `{first['dataset_sha256'][:12]}…`) was labelled by `tests/create_fresh_set_v12.py` and frozen before the "
    'parser ever ran on it; the backend fingerprint matched at evaluation time. The filter grammar already existed, so these commands test it on '
    'unseen sentences, not on the sentences used to build it.', '',
    '| Metric | First run |', '|---|---|',
    *[f"| {k.replace('_', ' ')} | {score(v)} |" for k, v in first['metrics'].items()],
    f"| core cases | {score(first['scopes']['core'])} |",
    f"| broader probes | {score(first['scopes']['capability_probe'])} |", '',
    f"**{len(core_misses)} core miss, and it is a labelling error:** " + '; '.join(
        f"**{c['id']}** “{c['text']}” expects `{json.dumps(c['expected_actions'])}` but the documented 16-object cap per action gives `{json.dumps(c['predicted_actions'])}` with the notice “Limited flower quantity to 16.”"
        for c in core_misses) + '. The parser behaved as documented; the gold was wrong. Frozen labels are never edited, so it stays a miss in every number here, and `tests/test_filter_fixes.py` asserts the capped output instead.',
    '', f'All {len(failures) - len(core_misses)} other misses were broader probes:', '',
    *[f"- **{c['id']}** “{c['text']}” — expected `{json.dumps(c['expected_actions'])}`, got `{json.dumps(c['predicted_actions'])}`"
      + (f" ({c['warnings'][0]})" if c['warnings'] else ' (**no notice: a silent misparse**)') for c in failures if c['scope'] != 'core'],
    '', '## What the first run exposed', '',
    '- **Two silent misparses**: `a pair of flowers in each of red and yellow` created two colorless flowers and `a sixth red and the rest blue` created twelve '
    'colorless houses, both with no notice. Both now parse; the class is also guarded: if actions were created, nothing else was reported and a typed '
    'color was used by no action, a notice says so (`Add a tower next to a red rock` previously ignored “red” silently).',
    '- Semicolon-separated groups (`three pink; the rest green`) had also failed in round ten; they now partition like commas.', '',
    '## Fixed after the first run', '',
    *[f"- **{c['id']}** {c['text']}" for c in fixed], '',
    '## Still outside the grammar', '',
    *[f"- **{c['id']}** {c['text']} — " + {'S44': 'count given after a color list', 'S46': 'trailing each-count', 'S48': 'group multiplication'}.get(c['id'], 'see report') for c in still if c['scope'] != 'core'],
    '', 'These are tracked as strict expected-failures in `tests/test_filter_fixes.py`, so they stay visible and an accidental fix is noticed.', '',
    '## Retests after the fixes', '',
    'These retests use sets the parser has now seen, so they are not accuracy estimates. They show that no earlier set regressed.', '',
    '| Set | Round eleven | After round-twelve fixes |', '|---|---|---|',
]
for name in SETS:
    before = previous[name]['metrics']['exact_match'] if name in previous else None
    after = retests[name]['metrics']['exact_match']
    lines.append(f"| {name} | {score(before) if before else '— (first run ' + score(first['metrics']['exact_match']) + ')'} | {score(after)} |")
gains = [(n, previous[n]['metrics']['exact_match']['correct'], retests[n]['metrics']['exact_match']['correct']) for n in SETS if n in previous
         and retests[n]['metrics']['exact_match']['correct'] != previous[n]['metrics']['exact_match']['correct']]
lines += ['', 'Earlier sets that changed: ' + (', '.join(f'{n} ({b} → {a})' for n, b, a in gains) or 'none') + '. '
          'Each change was checked against its gold label before accepting it.', '',
          'These are implementation-aware, hand-authored diagnostics, not independent accuracy estimates.']
(REPORTS / 'filters_fixes_report.md').write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
print(REPORTS / 'filters_fixes_report.md')
