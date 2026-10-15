"""Freeze tenth-round gold before any parser execution on these commands."""
import ast
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote
from tests.create_heldout_set import add,remove,setting,normalized
from tests.evaluate_heldout import pipeline_fingerprint

ROOT=Path(__file__).resolve().parents[1]
DESTINATION=Path(__file__).with_name('fresh_commands_v10.json')
CASES=[]


def case(text,category,actions,scope='core',note=''):
    CASES.append({'id':f'Q{len(CASES)+1:02d}','text':text,'category':category,'scope':scope,'expected_actions':actions,'label_note':note})


case('Create twelve flowers: one quarter pink and three quarters orange.', 'quarter_partition', [add('flower',3,'pink'),add('flower',9,'orange')])
case('Plant eight trees: two quarters green and half white.', 'mixed_fractions', [add('tree',4,'green'),add('tree',4,'white')])
case('Build sixteen homes: one quarter with orange roofs and the rest with purple roofs.', 'quarter_parts_remainder', [add('house',4,'orange'),add('house',12,'purple')])
case('Place twenty flowers: a quarter blue and three quarters yellow.', 'quarter_partition', [add('flower',5,'blue'),add('flower',15,'yellow')])
case('Plant four trees: one quarter of them blue and three quarters of them red.', 'quarter_them', [add('tree',1,'blue'),add('tree',3,'red')])
case('Create eight flowers: quarter purple, quarter pink, and half white.', 'mixed_fractions', [add('flower',2,'purple'),add('flower',2,'pink'),add('flower',4,'white')])
case('Build houses, a total of twelve: one quarter blue and the remainder green.', 'quarter_post_total', [add('house',3,'blue'),add('house',9,'green')])
case('Behind the lake, plant eight trees: a quarter orange and three-quarters white.', 'fronted_quarters', [add('tree',2,'orange','above','lake'),add('tree',6,'white','above','lake')])
case('Create zero flowers: one quarter white and three quarters pink.', 'zero_quarters', [])
case('Build ten houses: one quarter purple and three quarters yellow.', 'nonintegral_quarters', [])
case('Plant sixteen trees: three quarters blue and half pink.', 'overfull_quarters', [])
case('Place flowers: one quarter pink and three quarters purple.', 'undefined_quarters', [])
case('Add a flower of each color: purple, white and pink.', 'of_each_colors', [add('flower',1,'purple'),add('flower',1,'white'),add('flower',1,'pink')])
case('Plant four trees of each colour: yellow and green.', 'of_each_colors', [add('tree',4,'yellow'),add('tree',4,'green')])
case('Build exactly two homes of each color: orange, blue, and white.', 'of_each_list', [add('house',2,'orange'),add('house',2,'blue'),add('house',2,'white')])
case('Draw three flowers of each colour, pink and purple.', 'of_each_comma', [add('flower',3,'pink'),add('flower',3,'purple')])
case('Place a pair of houses of each color: white and green near the pond.', 'of_each_spatial', [add('house',2,'white','near','lake'),add('house',2,'green','near','lake')])
case('Plant half a dozen trees of each color: pink and white.', 'of_each_dozen', [add('tree',6,'pink'),add('tree',6,'white')])
case('Create one flower of each color: red and white; remove them.', 'of_each_references', [add('flower',1,'red'),add('flower',1,'white'),remove('flower',2)])
case('Add two flowers of each color: blue and gray.', 'unsupported_each_color', [])
case('Plant two green trees of each color: red and purple.', 'conflicting_each_color', [])
case('Add two flowers of each color: pink and purple and a house, all near the bridge.', 'of_each_mixed_tail', [add('flower',2,'pink','near','bridge'),add('flower',2,'purple','near','bridge'),add('house',relation='near',target='bridge')])
case('Place a flower and a tower, all behind the castle.', 'mixed_shared_location', [add('flower',relation='above',target='castle'),add('tower',relation='above',target='castle')])
case('Build two houses and plant three trees, all below the tower.', 'new_verb_tail_scope', [add('house',2),add('tree',3,relation='below',target='tower')], note='A new explicit verb begins a new clause; all applies to its sources only.')
case('Place two flowers and a rock, all between the house and the castle.', 'mixed_shared_between', [add('flower',2,relation='between',targets=['house','castle']),add('rock',relation='between',targets=['house','castle'])])
case('Draw a mountain and two white flowers, all right of the lake.', 'mixed_shared_location', [add('mountain',relation='right',target='lake'),add('flower',2,'white','right','lake')])
case('Build one home; plant two trees and a flower, all near it.', 'shared_singular_reference', [add('house'),add('tree',2,relation='near',target='house'),add('flower',relation='near',target='house')])
case('Build two cottages; add a flower and a tower, all between them.', 'shared_plural_reference', [add('house',2),add('flower',relation='between',targets=['house','house']),add('tower',relation='between',targets=['house','house'])])
case('Build eight houses: one quarter blue and three quarters white and three purple flowers, all near the road.', 'quarter_mixed_location', [add('house',2,'blue','near','road'),add('house',6,'white','near','road'),add('flower',3,'purple','near','road')])
case('Place a tower and two trees, all not near the river.', 'negated_shared_location', [])
case('Build a house beside the lake and two flowers, all left of the tower.', 'conflicting_shared_location', [])
case('Draw a rock and a mountain, all near.', 'missing_shared_landmark', [])
case('Build two houses whose roofs will already have been painted orange.', 'future_perfect', [add('house',2,'orange')])
case('Plant a tree whose foliage will have just been coloured red.', 'future_perfect_adverb', [add('tree',1,'red')])
case('Create flowers whose petals will have been freshly coloured yellow.', 'future_perfect_adverb', [add('flower',1,'yellow')])
case('Build a house with a roof that shall have been painted white behind the river.', 'future_perfect_spatial', [add('house',1,'white','above','river')])
case('Build four houses: one quarter whose roofs will have been painted pink and three quarters whose roofs will have been painted blue.', 'quarter_future_perfect', [add('house',1,'pink'),add('house',3,'blue')])
case('Build two houses whose roofs will have been coloured purple; remove them.', 'future_perfect_reference', [add('house',2,'purple'),remove('house',2)])
case('Build a cottage whose roof will not have been painted orange.', 'future_perfect_negation', [])
case('Create a castle whose petals will have been painted red.', 'future_perfect_unmapped', [])

case('Build cottages with a total of seven roofs painted red.', 'total_in_part', [add('house',7,'red')], 'capability_probe')
case('Plant twelve trees: one third purple and two thirds green.', 'third_distribution', [add('tree',4,'purple'),add('tree',8,'green')], 'capability_probe')
case('Build eight houses: two blue; the rest yellow.', 'semicolon_remainder', [add('house',2,'blue'),add('house',6,'yellow')], 'capability_probe')
case('Add flowers, two white and three pink; create one more of the former.', 'former_reference', [add('flower',2,'white'),add('flower',3,'pink'),add('flower',1,'white')], 'capability_probe')
case('Draw three clusters of four orange flowers.', 'group_multiplication', [add('flower',12,'orange')], 'capability_probe')
case('Preserve the castle while building three white cottages.', 'subordinate_creation', [add('house',3,'white')], 'capability_probe')
case('Create eight flowers: 25% pink and 75% purple.', 'percentage_distribution', [add('flower',2,'pink'),add('flower',6,'purple')], 'capability_probe')
case('Add flowers in red and blue, three of each.', 'trailing_each_count', [add('flower',3,'red'),add('flower',3,'blue')], 'capability_probe')
case('Build one pair of cottages in each of blue and green.', 'each_alternate_word_order', [add('house',2,'blue'),add('house',2,'green')], 'capability_probe')
case('Build a cottage that will have been painted blue.', 'whole_object_future_perfect', [add('house',1,'blue')], 'capability_probe')


if __name__ == '__main__':
    if DESTINATION.exists():
        raise SystemExit('Refusing to overwrite frozen round-ten labels.')
    known, inputs = set(), []
    for name in ['commands.json','heldout_commands.json'] + [f'fresh_commands_v{i}.json' for i in range(2,10)]:
        path = ROOT/'tests'/name
        inputs.append(path)
        data = json.loads(path.read_text(encoding='utf-8'))
        known.update(normalized(c['text']) for c in (data['cases'] if isinstance(data,dict) else data))
    for path in (ROOT/'tests').glob('test_*.py'):
        inputs.append(path)
        known.update(normalized(n.value) for n in ast.walk(ast.parse(path.read_text(encoding='utf-8'))) if isinstance(n,ast.Constant) and isinstance(n.value,str))
    for path in [ROOT/'frontend/tests/browser/smoke.spec.js',ROOT/'frontend/tests/browser/mobile.spec.js',ROOT/'frontend/scripts/capture-readme.mjs',ROOT/'frontend/src/world.js',ROOT/'README.md',ROOT/'docs/DEVELOPMENT.md']:
        inputs.append(path)
        content=path.read_text(encoding='utf-8-sig')
        known.update(normalized(m.group(2)) for m in re.finditer(r"(['\"])([^\n]*?)\1",content))
        known.update(normalized(line) for line in content.splitlines())
        known.update(normalized(unquote(s)) for s in re.findall(r'[?&]command=([^\s)"<>]+)',content))
    texts=[normalized(c['text']) for c in CASES]
    assert len(CASES)==len(set(texts))==50
    assert not set(texts)&known, f'Previously used commands: {set(texts)&known}'
    assert sum(c['scope']=='core' for c in CASES)==40
    pipeline,sources=pipeline_fingerprint()
    dataset={
        'name':'WordWorld tenth fresh 50-command evaluation — 2026-10-15',
        'method':'50 newly hand-authored commands and expected actions frozen before first prediction after quarter/of-each-color/mixed-location/future-perfect fixes. Author saw implementation and prior errors; not independently human-labeled or randomly sampled. No tuning on round-ten predictions.',
        'scope':'40 preassigned core cases and 10 broader probes. Core includes zero/negation, nonintegral/undefined/inconsistent fractions, invalid each colors, missing/conflicting placements and unmapped future-perfect colors. Fractions need a declared total giving whole objects; shared tails apply to one creation clause, resolved before new sources. Per-action cap remains 16. Sprite size, geometry and cross-request reference are not scored.',
        'gold_policy':'Exact ordered action dictionaries with aliases and the existing 16-per-action cap. Probe gold represents intended natural English, including forms outside the grammar. Each request starts with empty references; groups feed bounded removal and two-object references.',
        'parser_sha256_before':hashlib.sha256((ROOT/'backend/parser.py').read_bytes()).hexdigest(),
        'pipeline_sha256_before':pipeline,'source_files_sha256':sources,
        'uniqueness':'No normalized exact overlaps with all ten earlier datasets, Python test literals, browser smoke/capture and UI example literals, README/archive lines or decoded command links at freeze time. Similar grammar is intentional; semantic independence is not claimed.',
        'development_inputs_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        'cases':CASES,
    }
    DESTINATION.write_text(json.dumps(dataset,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print('Frozen 50 new commands; no parser execution occurred during labeling.')
    print('Dataset SHA256:',hashlib.sha256(DESTINATION.read_bytes()).hexdigest())
    print('Parser SHA256:',dataset['parser_sha256_before'])
    print('Backend pipeline SHA256:',pipeline)
