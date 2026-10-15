"""Freeze seventh-round gold actions before any predictions on this sample."""
import ast
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote
from tests.create_heldout_set import add, remove, setting, normalized
from tests.evaluate_heldout import pipeline_fingerprint

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = Path(__file__).with_name('fresh_commands_v7.json')
CASES = []


def case(text, category, actions, scope='core', note=''):
    CASES.append({'id':f'M{len(CASES)+1:02d}', 'text':text, 'category':category,
                  'scope':scope, 'expected_actions':actions, 'label_note':note})


case('Create seven cottages: three orange and four white.', 'colon_partition', [add('house',3,'orange'),add('house',4,'white')])
case('Plant flowers: two purple, three pink, and one yellow.', 'colon_partition', [add('flower',2,'purple'),add('flower',3,'pink'),add('flower',1,'yellow')])
case('Draw four trees: one with blue leaves and three with green leaves.', 'colon_parts', [add('tree',1,'blue'),add('tree',3,'green')])
case('Build six homes: two whose roofs are pink and four whose roofs are yellow.', 'colon_relatives', [add('house',2,'pink'),add('house',4,'yellow')])
case('Place five blue flowers: two small ones and three large ones.', 'shared_color', [add('flower',2,'blue'),add('flower',3,'blue')])
case('Build four houses with white roofs: one small one and three large ones.', 'post_color_partition', [add('house',1,'white'),add('house',3,'white')])
case('Plant three trees: zero yellow and three purple.', 'partition_zero', [add('tree',3,'purple')])
case('Place trees: not two white and four green.', 'partition_negation', [add('tree',4,'green')])
case('Draw three flowers: one orange and two pink beside the pond.', 'colon_spatial', [add('flower',1,'orange','near','lake'),add('flower',2,'pink','near','lake')])
case('To the left of the castle, build four houses: one white and three yellow.', 'fronted_colon', [add('house',1,'white','left','castle'),add('house',3,'yellow','left','castle')])
case('Create trees, a total of eight.', 'total_of', [add('tree',8)])
case('Place bridges, a total of exactly two across the creek.', 'total_of_spatial', [add('bridge',2,relation='across',target='river')])
case('Build cottages, the total of three.', 'total_of', [add('house',3)])
case('Draw rocks: a total of a dozen.', 'total_of', [add('rock',12)])
case('Add mountains, a total of half a dozen behind the tower.', 'total_of_spatial', [add('mountain',6,relation='above',target='tower')])
case('Create flowers, a total of two pairs.', 'total_of', [add('flower',4)])
case('Place roads, a total of nineteen.', 'total_cap', [add('road',16)], note='Existing 16-per-action cap.')
case('Draw towers, a total of zero.', 'total_zero', [])
case('Place castles, a total of -2.', 'invalid_total', [])
case('Build homes, a total of 2.5.', 'invalid_total', [])
case('Plant flowers, a total of four or seven.', 'ambiguous_total', [])
case('Add rocks, never a total of six.', 'negated_total', [])
case('Create flowers, a total of six: two yellow and four orange.', 'total_colon', [add('flower',2,'yellow'),add('flower',4,'orange')])
case('Build houses, a total of seven: four red and the remaining three white.', 'total_remainder', [add('house',4,'red'),add('house',3,'white')])
case('Plant eight trees, three purple and the remaining five green.', 'comma_remainder', [add('tree',3,'purple'),add('tree',5,'green')])
case('Create six flowers: one red, two yellow, and the remaining three pink.', 'multi_remainder', [add('flower',1,'red'),add('flower',2,'yellow'),add('flower',3,'pink')])
case('Build four cottages: one with a green roof and remaining three with orange roofs.', 'remainder_parts', [add('house',1,'green'),add('house',3,'orange')])
case('Plant three blue trees: one small one and the remaining two large ones.', 'remainder_shared', [add('tree',1,'blue'),add('tree',2,'blue')])
case('Add two white flowers: two small ones and remaining zero large ones.', 'remainder_zero', [add('flower',2,'white')])
case('Near the river, place five houses: one purple and the remaining four blue.', 'fronted_remainder', [add('house',1,'purple','near','river'),add('house',4,'blue','near','river')])
case('Build houses, a total of two: one red and the remaining one pink; put a tower between them.', 'remainder_reference', [add('house',1,'red'),add('house',1,'pink'),add('tower',relation='between',targets=['house','house'])])
case('Create four trees: one white and remaining three blue; remove two of them; remove them.', 'remainder_removal', [add('tree',1,'white'),add('tree',3,'blue'),remove('tree',2),remove('tree',2)])
case('Clear the world; place flowers, a total of three: one yellow and the remaining two purple; remove them.', 'reset_reference', [{'action':'reset'},add('flower',1,'yellow'),add('flower',2,'purple'),remove('flower',3)])
case('Keep the castle; draw rocks, a total of four; make it snow.', 'preservation_settings', [add('rock',4),setting('weather','snow')])
case('Do not build six cottages: two red and the remaining four blue; plant a flower.', 'negated_partition', [add('flower')])
case('Build seven houses: two pink and the remaining four white.', 'mismatch_remainder', [])
case('Plant flowers: two yellow and the remaining three green.', 'undefined_remainder', [])
case('Create five trees: remaining two green and three orange.', 'nonfinal_remainder', [])
case('Build four houses: one red and remaining one blue and remaining two green.', 'duplicate_remainder', [])
case('Place three houses: four large ones.', 'mismatch_ones', [])

case('Plant seven trees: two purple and the rest green.', 'inferred_remainder', [add('tree',2,'purple'),add('tree',5,'green')], 'capability_probe')
case('Build houses with a total of five roofs painted blue.', 'total_preposition', [add('house',5,'blue')], 'capability_probe')
case('Place six flowers: three each of pink and white.', 'distributive_quantity', [add('flower',3,'pink'),add('flower',3,'white')], 'capability_probe')
case('Create four cottages: one red; the remaining three blue.', 'semicolon_partition', [add('house',1,'red'),add('house',3,'blue')], 'capability_probe')
case('Add a cottage whose roof has recently been coloured orange.', 'passive_adverb', [add('house',1,'orange')], 'capability_probe')
case('Plant four trees: one green and three blue, all beside the river.', 'comma_shared_tail', [add('tree',1,'green','near','river'),add('tree',3,'blue','near','river')], 'capability_probe')
case('Build cottages, two yellow and one pink; add another of the latter.', 'latter_reference', [add('house',2,'yellow'),add('house',1,'pink'),add('house',1,'pink')], 'capability_probe')
case('Create three rows of two purple trees.', 'group_multiplication', [add('tree',6,'purple')], 'capability_probe')
case('Keep the lake unchanged while planting three pink flowers.', 'subordinate_creation', [add('flower',3,'pink')], 'capability_probe')
case('Bring back daylight and turn off the rain.', 'settings_paraphrase', [setting('time','day'),setting('weather','clear')], 'capability_probe')


if __name__ == '__main__':
    if DESTINATION.exists():
        raise SystemExit('Refusing to overwrite frozen round-seven labels.')
    known, inputs = set(), []
    for name in ['commands.json','heldout_commands.json'] + [f'fresh_commands_v{i}.json' for i in range(2,7)]:
        path = ROOT/'tests'/name
        inputs.append(path)
        data = json.loads(path.read_text(encoding='utf-8'))
        known.update(normalized(c['text']) for c in (data['cases'] if isinstance(data,dict) else data))
    for path in (ROOT/'tests').glob('test_*.py'):
        inputs.append(path)
        known.update(normalized(n.value) for n in ast.walk(ast.parse(path.read_text(encoding='utf-8'))) if isinstance(n,ast.Constant) and isinstance(n.value,str))
    for path in [ROOT/'frontend/tests/browser/smoke.spec.js',ROOT/'frontend/scripts/capture-readme.mjs',ROOT/'README.md',ROOT/'docs/DEVELOPMENT.md']:
        inputs.append(path)
        content = path.read_text(encoding='utf-8-sig')
        known.update(normalized(m.group(2)) for m in re.finditer(r"(['\"])([^\n]*?)\1",content))
        known.update(normalized(line) for line in content.splitlines())
        known.update(normalized(unquote(s)) for s in re.findall(r'[?&]command=([^\s)"<>]+)',content))
    texts = [normalized(c['text']) for c in CASES]
    assert len(CASES) == len(set(texts)) == 50
    assert not set(texts)&known, f'Previously used commands: {set(texts)&known}'
    assert sum(c['scope']=='core' for c in CASES) == 40
    pipeline, sources = pipeline_fingerprint()
    dataset = {
        'name':'WordWorld seventh fresh 50-command evaluation — 2026-10-15',
        'method':'50 newly hand-authored commands and expected actions frozen before first prediction after colon/total-of/remainder fixes. Author saw implementation and prior errors; not independently human-labeled or randomly sampled. No tuning on round-seven predictions.',
        'scope':'40 preassigned core cases and 10 broader probes. Core includes zero/negated groups, invalid/ambiguous quantities and inconsistent/undefined remainders. Explicit remaining counts must be final and sum to the declared total. Size rendering, geometry and cross-request reference are not scored.',
        'gold_policy':'Exact ordered action dictionaries with aliases and the existing 16-per-action cap. Probe gold represents natural intended English even outside implemented syntax. Each request starts with empty reference state; counted groups feed bounded removals and two-object references.',
        'parser_sha256_before':hashlib.sha256((ROOT/'backend/parser.py').read_bytes()).hexdigest(),
        'pipeline_sha256_before':pipeline, 'source_files_sha256':sources,
        'uniqueness':'No normalized exact overlaps with all seven earlier datasets, Python test string literals, browser smoke and capture literals, README/archive lines or decoded command links at freeze time. Similar grammar is intentional; semantic independence is not claimed.',
        'development_inputs_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        'cases':CASES,
    }
    DESTINATION.write_text(json.dumps(dataset,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(f'Frozen {len(CASES)} new commands: {DESTINATION}')
    print(f'Dataset SHA256: {hashlib.sha256(DESTINATION.read_bytes()).hexdigest()}')
    print(f'Parser SHA256: {dataset["parser_sha256_before"]}')
    print(f'Backend pipeline SHA256: {pipeline}')
    print('No parser execution occurred during labeling.')
