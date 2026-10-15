"""Freeze eighth-round gold actions before any predictions on this sample."""
import ast
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote
from tests.create_heldout_set import add, remove, setting, normalized
from tests.evaluate_heldout import pipeline_fingerprint

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = Path(__file__).with_name('fresh_commands_v8.json')
CASES = []


def case(text, category, actions, scope='core', note=''):
    CASES.append({'id':f'N{len(CASES)+1:02d}', 'text':text, 'category':category,
                  'scope':scope, 'expected_actions':actions, 'label_note':note})


case('Please switch the rain off.', 'weather_switch', [setting('weather','clear')])
case('Turn off the snow.', 'weather_switch', [setting('weather','clear')])
case('Please switch on rain.', 'weather_switch', [setting('weather','rain')])
case('Turn snow off; build a yellow house.', 'weather_object', [setting('weather','clear'),add('house',1,'yellow')])
case('Make it daylight and switch off the rain.', 'daylight_weather', [setting('time','day'),setting('weather','clear')])
case('Don’t switch on the snow; plant two green trees.', 'negated_switch', [add('tree',2,'green')])
case('Make it snow then turn the snow off.', 'weather_sequence', [setting('weather','snow'),setting('weather','clear')])
case('Turn rain on then switch rain off.', 'weather_sequence', [setting('weather','rain'),setting('weather','clear')])
case('Draw eight flowers: four each of red and white.', 'each_total', [add('flower',4,'red'),add('flower',4,'white')])
case('Plant trees: one each of orange, purple, and green.', 'each_list', [add('tree',1,'orange'),add('tree',1,'purple'),add('tree',1,'green')])
case('Place two each of blue and white houses.', 'each_prefix', [add('house',2,'blue'),add('house',2,'white')])
case('Add flowers, a pair each of purple and orange.', 'each_pairs', [add('flower',2,'purple'),add('flower',2,'orange')])
case('Build six homes: three each of green and pink beside the pond.', 'each_spatial', [add('house',3,'green','near','lake'),add('house',3,'pink','near','lake')])
case('Add flowers: no two each of pink and blue.', 'each_negation', [])
case('Create zero each of yellow and blue flowers.', 'each_zero', [])
case('Plant trees: half a dozen each of blue and white.', 'each_dozen', [add('tree',6,'blue'),add('tree',6,'white')])
case('Build nine houses: three each of purple, orange and yellow; remove them.', 'each_references', [add('house',3,'purple'),add('house',3,'orange'),add('house',3,'yellow'),remove('house',9)])
case('Draw five flowers: two each of pink and green.', 'each_mismatch', [])
case('Place six flowers: four orange and the rest pink.', 'inferred_rest', [add('flower',4,'orange'),add('flower',2,'pink')])
case('Build seven houses, two blue and the remainder purple.', 'inferred_remainder', [add('house',2,'blue'),add('house',5,'purple')])
case('Plant eight blue trees: three small ones and the rest large ones.', 'inferred_shared', [add('tree',3,'blue'),add('tree',5,'blue')])
case('Create flowers, a total of eight: three purple and the remaining ones white.', 'inferred_post_total', [add('flower',3,'purple'),add('flower',5,'white')])
case('Build two cottages: one orange and the rest white; place a rock between them.', 'inferred_between', [add('house',1,'orange'),add('house',1,'white'),add('rock',relation='between',targets=['house','house'])])
case('Plant four trees: one yellow and the rest pink; remove two of them; remove them.', 'inferred_removal', [add('tree',1,'yellow'),add('tree',3,'pink'),remove('tree',2),remove('tree',2)])
case('Place three flowers: three blue and the rest white.', 'inferred_zero', [add('flower',3,'blue')])
case('Create trees: one orange and the remainder green.', 'undefined_remainder', [])
case('Build two cottages: three red and the remaining ones white.', 'negative_remainder', [])
case('Place six flowers: the rest pink and two purple.', 'nonfinal_remainder', [])
case('Plant seven trees: one blue, the rest green, and the remainder yellow.', 'duplicate_remainder', [])
case('Switch off snow; build five homes: two purple and the rest yellow.', 'weather_partition', [setting('weather','clear'),add('house',2,'purple'),add('house',3,'yellow')])
case('Build two houses whose roofs have recently been painted green.', 'passive_adverb', [add('house',2,'green')])
case('Place a cottage whose roof has already been coloured purple.', 'passive_adverb', [add('house',1,'purple')])
case('Plant three trees whose leaves have just been colored orange.', 'passive_adverb', [add('tree',3,'orange')])
case('Create two flowers whose petals are newly painted pink.', 'passive_adverb', [add('flower',2,'pink')])
case('Build homes with roofs that had previously been painted blue.', 'passive_adverb', [add('house',1,'blue')])
case('Add flowers with petals which are freshly painted yellow.', 'passive_adverb', [add('flower',1,'yellow')])
case('Build four homes: one whose roof has already been painted blue and the rest whose roofs have recently been painted red.', 'passive_inferred', [add('house',1,'blue'),add('house',3,'red')])
case('Place a house whose roof has not recently been painted orange.', 'passive_negation', [])
case('Create a stone whose roof has already been coloured yellow.', 'unmapped_part', [])
case('Behind the lake, build two houses whose roofs have been freshly painted white.', 'passive_spatial', [add('house',2,'white','above','lake')])

case('Build cottages with a total of six roofs painted purple.', 'total_in_part', [add('house',6,'purple')], 'capability_probe')
case('Add eight flowers: half pink and half white.', 'fractional_distribution', [add('flower',4,'pink'),add('flower',4,'white')], 'capability_probe')
case('Plant trees: two green and three purple, all behind the tower.', 'comma_shared_tail', [add('tree',2,'green','above','tower'),add('tree',3,'purple','above','tower')], 'capability_probe')
case('Create five houses: two orange; the rest white.', 'semicolon_remainder', [add('house',2,'orange'),add('house',3,'white')], 'capability_probe')
case('Build a house whose roof will be painted pink.', 'future_passive', [add('house',1,'pink')], 'capability_probe')
case('Plant trees, one yellow and two green; add one more of the former.', 'former_reference', [add('tree',1,'yellow'),add('tree',2,'green'),add('tree',1,'yellow')], 'capability_probe')
case('Create four clusters of two white flowers.', 'group_multiplication', [add('flower',8,'white')], 'capability_probe')
case('Leave the river untouched while drawing two blue houses.', 'subordinate_creation', [add('house',2,'blue')], 'capability_probe')
case('Make it dawn and stop the storm.', 'setting_paraphrase', [setting('time','day'),setting('weather','clear')], 'capability_probe')
case('Build four houses: two with blue roofs and the others green.', 'others_remainder', [add('house',2,'blue'),add('house',2,'green')], 'capability_probe')


if __name__ == '__main__':
    if DESTINATION.exists():
        raise SystemExit('Refusing to overwrite frozen round-eight labels.')
    known, inputs = set(), []
    for name in ['commands.json','heldout_commands.json'] + [f'fresh_commands_v{i}.json' for i in range(2,8)]:
        path = ROOT/'tests'/name
        inputs.append(path)
        data = json.loads(path.read_text(encoding='utf-8'))
        known.update(normalized(c['text']) for c in (data['cases'] if isinstance(data,dict) else data))
    for path in (ROOT/'tests').glob('test_*.py'):
        inputs.append(path)
        known.update(normalized(n.value) for n in ast.walk(ast.parse(path.read_text(encoding='utf-8'))) if isinstance(n,ast.Constant) and isinstance(n.value,str))
    for path in [ROOT/'frontend/tests/browser/smoke.spec.js',ROOT/'frontend/scripts/capture-readme.mjs',ROOT/'frontend/src/world.js',ROOT/'README.md',ROOT/'docs/DEVELOPMENT.md']:
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
        'name':'WordWorld eighth fresh 50-command evaluation — 2026-10-15',
        'method':'50 newly hand-authored commands and expected actions frozen before first prediction after weather/each/inferred-remainder/passive-adverb fixes. Author saw implementation and prior errors; not independently human-labeled or randomly sampled. No tuning on round-eight predictions.',
        'scope':'40 preassigned core cases and 10 broader probes. Core includes zero/negation, inconsistent or undefined remainders, mismatched distributions and unmapped part colors. Inferred remainders require one declared total and a single final remainder. Per-action cap remains 16. Sprite size, geometry and cross-request reference are not scored.',
        'gold_policy':'Exact ordered action dictionaries with aliases and the existing 16-per-action cap. Probe gold represents intended natural English, including forms outside the grammar. Each request starts with empty references; groups feed bounded removal and two-object references.',
        'parser_sha256_before':hashlib.sha256((ROOT/'backend/parser.py').read_bytes()).hexdigest(),
        'pipeline_sha256_before':pipeline,'source_files_sha256':sources,
        'uniqueness':'No normalized exact overlaps with all eight earlier datasets, Python test literals, browser smoke/capture and UI example literals, README/archive lines or decoded command links at freeze time. Similar grammar is intentional; semantic independence is not claimed.',
        'development_inputs_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        'cases':CASES,
    }
    DESTINATION.write_text(json.dumps(dataset,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print('Frozen 50 new commands; no parser execution occurred during labeling.')
    print('Dataset SHA256:',hashlib.sha256(DESTINATION.read_bytes()).hexdigest())
    print('Parser SHA256:',dataset['parser_sha256_before'])
    print('Backend pipeline SHA256:',pipeline)
