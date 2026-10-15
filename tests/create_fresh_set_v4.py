"""Freeze fourth-round labels and provenance before any parser predictions."""
import ast
import hashlib
import json
from pathlib import Path
import re

from tests.create_heldout_set import add, remove, setting, normalized
from tests.evaluate_heldout import pipeline_fingerprint

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = Path(__file__).with_name('fresh_commands_v4.json')
CASES = []


def case(text, category, actions, scope='core', note=''):
    CASES.append({'id': f'H{len(CASES)+1:02d}', 'text': text, 'category': category,
                  'scope': scope, 'expected_actions': actions, 'label_note': note})


case('Build four cottages whose roofs are purple.', 'postnoun_color', [add('house',4,'purple')])
case('Plant two trees with yellow foliage.', 'postnoun_color', [add('tree',2,'yellow')])
case('Create five flowers whose petals are white.', 'postnoun_color', [add('flower',5,'white')])
case('Place a cottage which is pink next to the stream.', 'postnoun_color_spatial', [add('house',1,'pink','near','river')])
case('Grow three trees having orange leaves.', 'postnoun_color', [add('tree',3,'orange')])
case('Add two blossoms in yellow.', 'postnoun_color', [add('flower',2,'yellow')])
case('Build a cabin with the roof is red.', 'postnoun_color', [add('house',1,'red')], note='A deliberately informal phrase within the implemented with + part + is grammar, not a claim of general relative-clause support.')
case('Place three flowers that are blue behind the tower.', 'postnoun_color_spatial', [add('flower',3,'blue','above','tower')])
case('Build cottages, four of them.', 'postnoun_quantity', [add('house',4)])
case('Place rocks, a pair of them.', 'postnoun_quantity', [add('rock',2)])
case('Plant trees, seven altogether.', 'postnoun_quantity', [add('tree',7)])
case('Add flowers, eleven in total.', 'postnoun_quantity', [add('flower',11)])
case('Build bridges, two pairs of them across the river.', 'postnoun_quantity_spatial', [add('bridge',4,relation='across',target='river')])
case('Place towers, half a dozen in total.', 'postnoun_quantity', [add('tower',6)])
case('Add stones, thirty-two of them.', 'postnoun_quantity', [add('rock',16)], note='Existing per-action cap applies to 32 requested objects.')
case('Create castles, three of them behind the pond.', 'postnoun_quantity_spatial', [add('castle',3,relation='above',target='lake')])
case('Build houses, zero in total; plant two pink flowers.', 'postnoun_quantity_negation', [add('flower',2,'pink')])
case('Add roads, -2 in total; create a tower.', 'postnoun_quantity_negation', [add('tower')])
case('Place two tiny and five large cottages.', 'colorless_coordination', [add('house',2),add('house',5)])
case('Plant a pair of little and four big trees.', 'colorless_coordination', [add('tree',2),add('tree',4)])
case('Create three small, two large, and a tiny tower.', 'colorless_coordination', [add('tower',3),add('tower',2),add('tower')])
case('Draw a small and a large bridge across the creek.', 'colorless_coordination_spatial', [add('bridge',1,relation='across',target='river'),add('bridge',1,relation='across',target='river')])
case('Place two small and four pink flowers.', 'mixed_coordination', [add('flower',2),add('flower',4,'pink')])
case('Build three red and two large homes.', 'mixed_coordination', [add('house',3,'red'),add('house',2)])
case('Add two small, one white, and three large trees.', 'mixed_coordination', [add('tree',2),add('tree',1,'white'),add('tree',3)])
case('Put a little and two large rocks near the bridge.', 'colorless_coordination_spatial', [add('rock',1,relation='near',target='bridge'),add('rock',2,relation='near',target='bridge')])
case('Build two small and not four large homes.', 'colorless_coordination_negation', [add('house',2)])
case('Plant zero small and two large trees with purple foliage.', 'shared_postnoun_color', [add('tree',2,'purple')])
case('Add cottages, three of them, whose roofs are white; remove two of them.', 'attributes_reference', [add('house',3,'white'),remove('house',2)])
case('Build a cottage which is orange; place two flowers near it.', 'attributes_reference', [add('house',1,'orange'),add('flower',2,relation='near',target='house')])
case('Place flowers with red petals, a pair of them beside the tower.', 'combined_attributes', [add('flower',2,'red','near','tower')])
case('Behind the castle, plant trees, a dozen of them, with green leaves.', 'combined_attributes', [add('tree',12,'green','above','castle')])
case('Build one tiny and one large cabin; add a road between them.', 'coordination_reference', [add('house'),add('house'),add('road',relation='between',targets=['house','house'])])
case('Create two little and three large houses whose roofs are orange.', 'shared_postnoun_color', [add('house',2,'orange'),add('house',3,'orange')])
case('Place flowers that are purple and two cottages with green roofs.', 'attribute_scope', [add('flower',1,'purple'),add('house',2,'green')])
case('Plant a tree near the cottage with orange roofs and two white flowers.', 'landmark_attribute_scope', [add('tree',1,relation='near',target='house'),add('flower',2,'white')], note='Named-type placement only: landmark color is not a selector and must not leak onto the flower subject.')
case('Keep the lake; build cottages, two of them, with yellow roofs.', 'preservation_attributes', [add('house',2,'yellow')])
case('Create trees, four of them, with blue leaves; make it night; remove them.', 'attributes_reference_settings', [add('tree',4,'blue'),setting('time','night'),remove('tree',4)])
case('Build houses with pink roofs, a pair of them; remove one of them; remove it.', 'attributes_reference', [add('house',2,'pink'),remove('house',1),remove('house',1)])
case('Add a cottage whose roof is purple; build a bridge spanning the creek.', 'attributes_relational_roles', [add('house',1,'purple'),add('bridge',relation='across',target='river')])

case('Add three houses with roofs painted blue.', 'painted_part_paraphrase', [add('house',3,'blue')], 'capability_probe')
case('Plant flowers, exactly five of them.', 'quantity_adverb', [add('flower',5)], 'capability_probe')
case('Build a house with a roof that is yellow.', 'nested_part_relative', [add('house',1,'yellow')], 'capability_probe')
case('Place two small houses and three large ones.', 'noun_ellipsis', [add('house',2),add('house',3)], 'capability_probe', 'Size rendering is not scored; the missing second object noun must inherit house.')
case('Build houses in two groups of three.', 'group_multiplication', [add('house',6)], 'capability_probe')
case('Plant two trees that are green and three that are yellow.', 'relative_clause_coordination', [add('tree',2,'green'),add('tree',3,'yellow')], 'capability_probe')
case('Add flowers, five in all.', 'quantity_tail_paraphrase', [add('flower',5)], 'capability_probe')
case('Build a house to the northern side of the pond.', 'direction_paraphrase', [add('house',1,relation='above',target='lake')], 'capability_probe')
case('Preserve the cottage while planting three trees.', 'subordinate_creation', [add('tree',3)], 'capability_probe')
case('Make it sunny with no precipitation.', 'weather_paraphrase', [setting('time','day'),setting('weather','clear')], 'capability_probe')


if __name__ == '__main__':
    if DESTINATION.exists():
        raise SystemExit('Refusing to overwrite frozen round-four labels.')
    known, inputs = set(), []
    for name in ['commands.json','heldout_commands.json','fresh_commands_v2.json','fresh_commands_v3.json']:
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
        'name':'WordWorld fourth fresh 50-command evaluation — 2026-10-15',
        'method':'50 newly hand-authored commands and expected actions frozen before prediction after post-noun/coordination fixes. Author saw implementation and prior results; not independently human-labeled or randomly sampled. No tuning on round-four results.',
        'scope':'40 preassigned core cases and 10 broader grammar probes. Request-local reference contract and existing count caps apply. Core includes two zero/negative-count refusal cases, one informal with+part+is phrase, and a named-type landmark case that does not test color filtering. Coordination scores count/color groups; sizes are not rendered or scored. Geometry and cross-request context are not scored.',
        'gold_policy':'Exact ordered action dictionaries. Shared post-noun color applies to separately counted groups. Appositive of them is a quantity marker, not a new source reference. Gold labels follow intended English for probes even when outside implemented grammar.',
        'parser_sha256_before':hashlib.sha256((ROOT/'backend/parser.py').read_bytes()).hexdigest(),
        'pipeline_sha256_before':pipeline,
        'source_files_sha256':sources,
        'uniqueness':'No normalized exact overlaps against all four previous sets, Python regression string literals, browser smoke-test string literals or README lines. Similar grammatical constructions are intentional; semantic independence is not claimed.',
        'development_inputs_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        'cases':CASES,
    }
    DESTINATION.write_text(json.dumps(dataset,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(f'Frozen {len(CASES)} new commands: {DESTINATION}')
    print(f'Dataset SHA256: {hashlib.sha256(DESTINATION.read_bytes()).hexdigest()}')
    print(f'Parser SHA256: {dataset["parser_sha256_before"]}')
    print(f'Backend pipeline SHA256: {pipeline}')
    print('No parser execution occurred during labeling.')
