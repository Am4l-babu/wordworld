"""Freeze ninth-round gold before any parser execution on these commands."""
import ast
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote
from tests.create_heldout_set import add,remove,setting,normalized
from tests.evaluate_heldout import pipeline_fingerprint

ROOT=Path(__file__).resolve().parents[1]
DESTINATION=Path(__file__).with_name('fresh_commands_v9.json')
CASES=[]


def case(text,category,actions,scope='core',note=''):
    CASES.append({'id':f'P{len(CASES)+1:02d}','text':text,'category':category,'scope':scope,'expected_actions':actions,'label_note':note})


case('End the storm.', 'weather_stop', [setting('weather','clear')])
case('Stop the shower.', 'weather_stop', [setting('weather','clear')])
case('Make it dawn and stop the rain.', 'dawn_stop', [setting('time','day'),setting('weather','clear')])
case('Never end the storm; plant two pink flowers.', 'negated_stop', [add('flower',2,'pink')])
case('Make it snow and end the snow.', 'weather_sequence', [setting('weather','snow'),setting('weather','clear')])
case('Stop storm; place a purple flower.', 'weather_object', [setting('weather','clear'),add('flower',1,'purple')])
case('Build twelve houses: half orange and half pink.', 'half_partition', [add('house',6,'orange'),add('house',6,'pink')])
case('Create fourteen flowers, half white and half purple.', 'half_partition', [add('flower',7,'white'),add('flower',7,'purple')])
case('Plant ten trees: half of them blue and half of them purple.', 'half_them', [add('tree',5,'blue'),add('tree',5,'purple')])
case('Draw flowers, a total of six: half orange and half red.', 'half_post_total', [add('flower',3,'orange'),add('flower',3,'red')])
case('Build four green houses: half small ones and half big ones.', 'half_shared_color', [add('house',2,'green'),add('house',2,'green')])
case('Build two cottages: half blue and half pink; put a rock between them.', 'half_between', [add('house',1,'blue'),add('house',1,'pink'),add('rock',relation='between',targets=['house','house'])])
case('Plant six trees: half orange and the rest white; remove them.', 'half_rest_reference', [add('tree',3,'orange'),add('tree',3,'white'),remove('tree',6)])
case('Add eight flowers: half yellow and half purple near the pond.', 'half_spatial', [add('flower',4,'yellow','near','lake'),add('flower',4,'purple','near','lake')])
case('Build nine houses: half blue and half orange.', 'odd_half_total', [])
case('Plant trees: half red and half white.', 'undefined_half_total', [])
case('Create six flowers: half pink, half blue, and half yellow.', 'overfull_half_total', [])
case('Place zero flowers: half red and half yellow.', 'zero_halves', [])
case('Build four homes: one blue and three white, all right of the lake.', 'shared_comma_location', [add('house',1,'blue','right','lake'),add('house',3,'white','right','lake')])
case('Plant trees: two each of pink and green, all behind the house.', 'shared_each_location', [add('tree',2,'pink','above','house'),add('tree',2,'green','above','house')])
case('Place flowers: one white and two yellow, all near the bridge.', 'shared_comma_location', [add('flower',1,'white','near','bridge'),add('flower',2,'yellow','near','bridge')])
case('Build six houses: two orange and four green, all between the lake and the tower.', 'shared_between', [add('house',2,'orange','between',targets=['lake','tower']),add('house',4,'green','between',targets=['lake','tower'])])
case('Build two cottages, one pink and one orange, all across the river.', 'shared_across', [add('house',1,'pink','across','river'),add('house',1,'orange','across','river')])
case('Plant four trees: one blue and the rest green, all near the castle.', 'shared_inferred_location', [add('tree',1,'blue','near','castle'),add('tree',3,'green','near','castle')])
case('Create six flowers: half pink and half blue, all below the tower.', 'shared_half_location', [add('flower',3,'pink','below','tower'),add('flower',3,'blue','below','tower')])
case('Plant trees: two whose leaves are white and three whose leaves are purple, all left of the mountain.', 'shared_relative_location', [add('tree',2,'white','left','mountain'),add('tree',3,'purple','left','mountain')])
case('Build four houses: half pink and half white, all near.', 'missing_shared_landmark', [])
case('Create trees: two yellow and three green, all not near the castle.', 'negated_shared_location', [])
case('Place a house whose roof shall be painted yellow.', 'future_passive', [add('house',1,'yellow')])
case('Plant a tree whose leaves will be coloured pink.', 'future_passive', [add('tree',1,'pink')])
case('Create flowers whose petals will be freshly coloured purple.', 'future_adverb', [add('flower',1,'purple')])
case('Build two houses with roofs which will be painted green.', 'future_passive', [add('house',2,'green')])
case('Behind the lake, place a cottage whose roof will be colored blue.', 'fronted_future', [add('house',1,'blue','above','lake')])
case('Create a home with a roof that shall be painted orange.', 'future_part', [add('house',1,'orange')])
case('Build six houses: half whose roofs will be painted white and half whose roofs will be painted blue, all beside the pond.', 'half_future_shared', [add('house',3,'white','near','lake'),add('house',3,'blue','near','lake')])
case('Build four cottages: one whose roof will be painted pink and the rest whose roofs will be painted orange.', 'inferred_future', [add('house',1,'pink'),add('house',3,'orange')])
case('Add two houses whose roofs shall be painted white; remove them.', 'future_reference', [add('house',2,'white'),remove('house',2)])
case('Create a house whose roof will not be coloured purple.', 'future_negation', [])
case('Place a boulder whose leaves will be painted green.', 'future_unmapped_part', [])
case('Build a house whose roof will be painted yellow or purple.', 'future_ambiguous_color', [])

case('Build houses with a total of eight roofs painted white.', 'total_in_part', [add('house',8,'white')], 'capability_probe')
case('Plant eight trees: one quarter blue and three quarters white.', 'quarter_distribution', [add('tree',2,'blue'),add('tree',6,'white')], 'capability_probe')
case('Create six cottages: two green; the rest purple.', 'semicolon_remainder', [add('house',2,'green'),add('house',4,'purple')], 'capability_probe')
case('Add flowers, one yellow and two pink; create two more of the latter.', 'latter_reference', [add('flower',1,'yellow'),add('flower',2,'pink'),add('flower',2,'pink')], 'capability_probe')
case('Draw four bunches of three purple flowers.', 'group_multiplication', [add('flower',12,'purple')], 'capability_probe')
case('Keep the tower intact while planting four green trees.', 'subordinate_creation', [add('tree',4,'green')], 'capability_probe')
case('Build a cottage whose roof will have been painted white.', 'future_perfect', [add('house',1,'white')], 'capability_probe')
case('Plant six trees: two blue and the others purple.', 'others_remainder', [add('tree',2,'blue'),add('tree',4,'purple')], 'capability_probe')
case('Add three flowers of each color: red and white.', 'each_word_order', [add('flower',3,'red'),add('flower',3,'white')], 'capability_probe')
case('Build two blue houses and three yellow flowers, all beside the lake.', 'mixed_type_shared_location', [add('house',2,'blue','near','lake'),add('flower',3,'yellow','near','lake')], 'capability_probe')


if __name__ == '__main__':
    if DESTINATION.exists():
        raise SystemExit('Refusing to overwrite frozen round-nine labels.')
    known, inputs = set(), []
    for name in ['commands.json','heldout_commands.json'] + [f'fresh_commands_v{i}.json' for i in range(2,9)]:
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
        'name':'WordWorld ninth fresh 50-command evaluation — 2026-10-15',
        'method':'50 newly hand-authored commands and expected actions frozen before first prediction after storm/half/shared-location/future-passive fixes. Author saw implementation and prior errors; not independently human-labeled or randomly sampled. No tuning on round-nine predictions.',
        'scope':'40 preassigned core cases and 10 broader probes. Core includes zero/negation, odd/undefined/inconsistent half totals, missing landmarks and unmapped/ambiguous future part colors. Halves require an even declared total; shared comma tails apply to one same-noun collection. Per-action cap remains 16. Sprite size, geometry and cross-request reference are not scored.',
        'gold_policy':'Exact ordered action dictionaries with aliases and the existing 16-per-action cap. Probe gold represents intended natural English, including forms outside the grammar. Each request starts with empty references; groups feed bounded removal and two-object references.',
        'parser_sha256_before':hashlib.sha256((ROOT/'backend/parser.py').read_bytes()).hexdigest(),
        'pipeline_sha256_before':pipeline,'source_files_sha256':sources,
        'uniqueness':'No normalized exact overlaps with all nine earlier datasets, Python test literals, browser smoke/capture and UI example literals, README/archive lines or decoded command links at freeze time. Similar grammar is intentional; semantic independence is not claimed.',
        'development_inputs_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        'cases':CASES,
    }
    DESTINATION.write_text(json.dumps(dataset,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print('Frozen 50 new commands; no parser execution occurred during labeling.')
    print('Dataset SHA256:',hashlib.sha256(DESTINATION.read_bytes()).hexdigest())
    print('Parser SHA256:',dataset['parser_sha256_before'])
    print('Backend pipeline SHA256:',pipeline)
