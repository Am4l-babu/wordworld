"""Round eleven: language edits, cross-request references and fractions.

Run from the project root after `python -m tests.create_fresh_set_v11` froze the labels and the
first evaluation wrote evaluation/results/fresh_results_v11.json:

    python -m evaluation.scripts.write_edits_report

It retests every saved set with the current parser, stores those retests separately from the
first-run predictions, and renders evaluation/reports/edits_fixes_report.md.
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
SETS = ['heldout'] + [f'fresh_v{i}' for i in range(2, 12)]
PREVIOUS = {'heldout': 'heldout_retest_v10.json', **{f'fresh_v{i}': f'fresh_v{i}_retest_v10.json' for i in range(2, 10)}, 'fresh_v10': 'fresh_results_v10.json'}


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


first = json.loads((HERE / 'fresh_results_v11.json').read_text(encoding='utf-8'))
assert first['matches_frozen_parser'] and first['evaluation_kind'] == 'frozen new-command evaluation'
retests = retest_all()
(HERE / 'round11_after_fix_retests.json').write_text(json.dumps(retests, indent=2, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')
failures = [c for c in first['cases'] if not c['exact_match']]
lines = [
    '# Round eleven: language edits, cross-request references and fractions', '',
    'This round adds edits of existing objects (recolor, resize, move by landmark or direction), references that carry across '
    'requests through client context, and thirds/fifths/tenths/percentages in counted partitions.', '',
    '## Frozen first run', '',
    f"`tests/fresh_commands_v11.json` (SHA-256 `{first['dataset_sha256'][:12]}…`) was labelled by `tests/create_fresh_set_v11.py` and frozen "
    'before the parser ever ran on it; the backend fingerprint matched at evaluation time. Cases with a `context` field pass it to the '
    'parser exactly as the browser would.', '',
    '| Metric | First run |', '|---|---|',
    *[f"| {k.replace('_', ' ')} | {score(v)} |" for k, v in first['metrics'].items()],
    f"| core cases | {score(first['scopes']['core'])} |",
    f"| broader probes | {score(first['scopes']['capability_probe'])} |",
    '', f'All 40 core cases were exact on first sight; {len(failures)} of 10 broader probes failed:', '',
    *[f"- **{c['id']}** “{c['text']}” — expected `{json.dumps(c['expected_actions'])}`, got `{json.dumps(c['predicted_actions'])}` ({c['outcome']})" for c in failures],
    '', 'Two of these were wrong actions rather than abstentions: “make both houses green” and “make the houses a bit taller” created a '
    'house. Both now edit existing houses.', '',
    '## Fixes after the first run', '',
    '- `both` and `the two …` name existing objects; `taller`, `shorter`, `wider` resize',
    '- `closer to` is a `near` relation; an amount may follow a direction (`up a little`) or precede a place (`a little closer to the house`)',
    '- `give the cottage a red roof` recolors the part a sprite draws; `give me two houses` still creates',
    '', '## Retests after the fixes', '',
    'These retests use sets the parser has now seen, so they are not accuracy estimates. They show that no earlier set regressed.', '',
    '| Set | Round ten | After round-eleven fixes |', '|---|---|---|',
]
for name in SETS:
    before = json.loads((HERE / PREVIOUS[name]).read_text(encoding='utf-8'))['metrics']['exact_match'] if name in PREVIOUS else None
    after = retests[name]['metrics']['exact_match']
    lines.append(f"| {name} | {score(before) if before else '— (first run ' + score(first['metrics']['exact_match']) + ')'} | {score(after)} |")
lines += ['', 'The two fresh-v10 gains are the fraction fixes (`one third purple and two thirds green`, `25% pink and 75% purple`).', '',
          'These are implementation-aware, hand-authored diagnostics, not independent accuracy estimates.']
(REPORTS / 'edits_fixes_report.md').write_text('\n'.join(line for line in lines if line is not None) + '\n', encoding='utf-8', newline='\n')
print(REPORTS / 'edits_fixes_report.md')
