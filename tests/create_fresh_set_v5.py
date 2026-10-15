"""Freeze fifth-round gold labels and provenance without executing the parser."""
import ast
import hashlib
import json
from pathlib import Path
import re

from tests.create_heldout_set import add, remove, setting, normalized
from tests.evaluate_heldout import pipeline_fingerprint

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = Path(__file__).with_name('fresh_commands_v5.json')
CASES = []


def case(text, category, actions, scope='core', note=''):
    CASES.append({'id': f'J{len(CASES)+1:02d}', 'text':text, 'category':category,
                  'scope':scope, 'expected_actions':actions, 'label_note':note})


case('Add flowers, exactly eight in all.', 'exact_quantities', [add('flower',8)])
case('Plant trees, exactly a pair in all.', 'exact_quantities', [add('tree',2)])
case('Place cottages, exactly eleven of them.', 'exact_quantities', [add('house',11)])
case('Add boulders, exactly half a dozen in total.', 'exact_quantities', [add('rock',6)])
case('Create towers, exactly three in all.', 'exact_quantities', [add('tower',3)])
case('Build bridges, exactly two of them across the stream.', 'exact_quantities_spatial', [add('bridge',2,relation='across',target='river')])
case('Add flowers, exactly eighteen in all.', 'exact_quantities', [add('flower',16)], note='Existing 16-per-action cap applies.')
case('Create exactly four white flowers near the castle.', 'exact_quantities_spatial', [add('flower',4,'white','near','castle')])
case('Build three homes with roofs painted pink.', 'roof_clauses', [add('house',3,'pink')])
case('Place a cabin with a roof which is painted green.', 'roof_clauses', [add('house',1,'green')])
case('Add a cottage whose roof is coloured white.', 'roof_clauses', [add('house',1,'white')])
case('Build a home which has an orange roof.', 'roof_clauses', [add('house',1,'orange')])
case('Add a house with roofs that are painted red.', 'roof_clauses', [add('house',1,'red')])
case('Plant two trees with leaves painted purple.', 'part_color_clauses', [add('tree',2,'purple')])
case('Place three flowers with petals which are blue.', 'part_color_clauses', [add('flower',3,'blue')])
case('Build a house with a roof that is yellow and two trees with green foliage.', 'part_color_scope', [add('house',1,'yellow'),add('tree',2,'green')])
case('Place three small towers and two large ones.', 'noun_ellipsis', [add('tower',3),add('tower',2)])
case('Draw two short bridges and a tall one over the creek.', 'noun_ellipsis_spatial', [add('bridge',2,relation='across',target='river'),add('bridge',1,relation='across',target='river')], note='A trailing relation is shared by the adjacent groups under the documented grammar. Size rendering is not scored.')
case('Add a rock and three small ones.', 'noun_ellipsis', [add('rock'),add('rock',3)])
case('Plant four trees and a pair of blue ones.', 'noun_ellipsis', [add('tree',4),add('tree',2,'blue')])
case('Build two white cottages and one pink one.', 'noun_ellipsis', [add('house',2,'white'),add('house',1,'pink')])
case('Add two tiny castles, three big ones, and a little one.', 'noun_ellipsis', [add('castle',2),add('castle',3),add('castle')])
case('Place two flowers and four purple ones beside the castle.', 'noun_ellipsis_spatial', [add('flower',2,relation='near',target='castle'),add('flower',4,'purple','near','castle')])
case('Build one house and zero big ones.', 'noun_ellipsis_negation', [add('house')])
case('Build no homes and three yellow ones.', 'noun_ellipsis_negation', [add('house',3,'yellow')])
case('Plant three trees that are pink and two which are blue.', 'relative_coordination', [add('tree',3,'pink'),add('tree',2,'blue')])
case('Add one house whose roof is white and two whose roofs are orange.', 'relative_coordination', [add('house',1,'white'),add('house',2,'orange')])
case('Place four flowers that are yellow, two that are pink, and three that are white.', 'relative_coordination', [add('flower',4,'yellow'),add('flower',2,'pink'),add('flower',3,'white')])
case('Build two cottages with blue roofs and one whose roof is painted purple.', 'relative_coordination', [add('house',2,'blue'),add('house',1,'purple')])
case('Plant two trees that are green and not four that are yellow.', 'relative_coordination_negation', [add('tree',2,'green')])
case('Create one house and one whose roof is painted red near the lake.', 'relative_coordination_spatial', [add('house',1,relation='near',target='lake'),add('house',1,'red','near','lake')])
case('Add two trees with pink leaves and three blue ones.', 'mixed_continuations', [add('tree',2,'pink'),add('tree',3,'blue')])
case('Build one pink house and one blue one; put a flower between them.', 'continuation_references', [add('house',1,'pink'),add('house',1,'blue'),add('flower',relation='between',targets=['house','house'])])
case('Add flowers, exactly seven in all; remove two of them; remove them.', 'quantity_references', [add('flower',7),remove('flower',2),remove('flower',5)])
case('Build three houses with red roofs and two large ones; remove them.', 'continuation_references', [add('house',3,'red'),add('house',2),remove('house',5)], note='Ones inherits only the source noun type; omitted color uses the existing default.')
case('Near the castle, build a house with a roof which is green and two large ones.', 'fronted_continuations', [add('house',1,'green','near','castle'),add('house',2,relation='near',target='castle')])
case('Preserve the flowers; add trees, exactly five in all; make it night.', 'quantities_settings', [add('tree',5),setting('time','night')])
case('Grow two trees that are green and three that are purple; remove two of them.', 'relative_references', [add('tree',2,'green'),add('tree',3,'purple'),remove('tree',2)])
case('Don’t add cottages with roofs painted red; add flowers, exactly four in total.', 'negation_quantities', [add('flower',4)])
case('Build a house with a blue roof; reset; remove it.', 'reference_reset', [add('house',1,'blue'),{'action':'reset'}], note='Reset invalidates the antecedent; the final removal must abstain.')

case('Add trees, two that are green and three that are yellow.', 'postnoun_partition', [add('tree',2,'green'),add('tree',3,'yellow')], 'capability_probe', 'A bare plural followed by counted descriptions specifies the complete collection; do not add an extra default tree.')
case('Build exactly five blue-roofed cottages.', 'compound_adjective', [add('house',5,'blue')], 'capability_probe')
case('Build a house whose roof has been painted red.', 'passive_roof_clause', [add('house',1,'red')], 'capability_probe')
case('Add flowers, five total.', 'quantity_tail_variant', [add('flower',5)], 'capability_probe')
case('Plant two trees that are green and three yellow.', 'predicate_ellipsis', [add('tree',2,'green'),add('tree',3,'yellow')], 'capability_probe')
case('Place two houses, one with a blue roof and one with a green roof.', 'partitioned_roof_groups', [add('house',1,'blue'),add('house',1,'green')], 'capability_probe', 'The two later groups partition the explicit total of two houses; no extra default group is requested.')
case('Build two cottages near the lake; add three large ones behind the tower.', 'cross_clause_ellipsis', [add('house',2,relation='near',target='lake'),add('house',3,relation='above',target='tower')], 'capability_probe', 'Natural-English noun-type inheritance across an explicit new verb is broader than the documented adjacent-group contract; gold requests houses, never a new tower.')
case('Create castles in three groups of two.', 'group_multiplication', [add('castle',6)], 'capability_probe')
case('Keep the flowers while adding two blue houses.', 'subordinate_creation', [add('house',2,'blue')], 'capability_probe')
case('Make it daylight and stop the snow.', 'setting_paraphrase', [setting('time','day'),setting('weather','clear')], 'capability_probe')


if __name__ == '__main__':
    if DESTINATION.exists():
        raise SystemExit('Refusing to overwrite frozen round-five labels.')
    known, inputs = set(), []
    for name in ['commands.json','heldout_commands.json','fresh_commands_v2.json','fresh_commands_v3.json','fresh_commands_v4.json']:
        path = ROOT/'tests'/name
        inputs.append(path)
        data = json.loads(path.read_text(encoding='utf-8'))
        known.update(normalized(c['text']) for c in (data['cases'] if isinstance(data,dict) else data))
    for path in (ROOT/'tests').glob('test_*.py'):
        inputs.append(path)
        tree = ast.parse(path.read_text(encoding='utf-8'))
        known.update(normalized(node.value) for node in ast.walk(tree) if isinstance(node,ast.Constant) and isinstance(node.value,str))
    browser = ROOT/'frontend/tests/browser/smoke.spec.js'
    readme = ROOT/'README.md'
    inputs.extend([browser,readme])
    known.update(normalized(m.group(2)) for m in re.finditer(r"(['\"])([^\n]*?)\1",browser.read_text(encoding='utf-8')))
    known.update(normalized(line) for line in readme.read_text(encoding='utf-8').splitlines())
    texts = [normalized(c['text']) for c in CASES]
    assert len(CASES) == len(set(texts)) == 50
    assert not set(texts)&known, f'Previously used commands: {set(texts)&known}'
    assert sum(c['scope']=='core' for c in CASES) == 40
    pipeline, sources = pipeline_fingerprint()
    dataset = {
        'name':'WordWorld fifth fresh 50-command evaluation — 2026-10-15',
        'method':'50 newly hand-authored commands and gold actions frozen before first prediction after quantity/roof/ellipsis fixes. Author saw implementation and prior failures; not independently human-labeled or randomly sampled. No tuning on round-five predictions.',
        'scope':'40 preassigned core cases and 10 broader probes. Core includes zero/negated count groups and one reset-reference refusal. Adjacent ones inherits a noun type, not existing object IDs or omitted colors. Trailing placement applies to adjacent groups; sizes are neither rendered nor scored. Scene geometry is not scored. Probe gold follows natural intended English, including partition and cross-clause forms beyond the bounded implemented contract.',
        'gold_policy':'Exact ordered action dictionaries; aliases and 16-per-action cap apply. Each request starts with empty discourse context. Settings preserve focus; reset clears it. Appositive them belongs to the count, not a source pronoun. All later removal/spatial references must retain groups introduced by coordinated descriptions.',
        'parser_sha256_before':hashlib.sha256((ROOT/'backend/parser.py').read_bytes()).hexdigest(),
        'pipeline_sha256_before':pipeline,
        'source_files_sha256':sources,
        'uniqueness':'No normalized exact overlap against the five earlier datasets, Python regression string literals, browser smoke-test literals or README lines at freeze time. Similar grammar is intentional; semantic independence is not claimed.',
        'development_inputs_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        'cases':CASES,
    }
    DESTINATION.write_text(json.dumps(dataset,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(f'Frozen {len(CASES)} new commands: {DESTINATION}')
    print(f'Dataset SHA256: {hashlib.sha256(DESTINATION.read_bytes()).hexdigest()}')
    print(f'Parser SHA256: {dataset["parser_sha256_before"]}')
    print(f'Backend pipeline SHA256: {pipeline}')
    print('No parser execution occurred during labeling.')
