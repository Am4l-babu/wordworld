"""Freeze sixth-round gold actions before any predictions on this sample."""
import ast
import hashlib
import json
from pathlib import Path
import re
from tests.create_heldout_set import add, remove, setting, normalized
from tests.evaluate_heldout import pipeline_fingerprint

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = Path(__file__).with_name('fresh_commands_v6.json')
CASES = []


def case(text, category, actions, scope='core', note=''):
    CASES.append({'id':f'L{len(CASES)+1:02d}', 'text':text, 'category':category,
                  'scope':scope, 'expected_actions':actions, 'label_note':note})


case('Plant trees, three green and two purple.', 'bare_partition', [add('tree',3,'green'),add('tree',2,'purple')])
case('Build houses, two with orange roofs and three with white roofs.', 'bare_partition', [add('house',2,'orange'),add('house',3,'white')])
case('Create flowers, four pink ones and two yellow ones.', 'bare_partition', [add('flower',4,'pink'),add('flower',2,'yellow')])
case('Place six cottages, two with blue roofs and four with green roofs.', 'declared_partition', [add('house',2,'blue'),add('house',4,'green')])
case('Add flowers, three whose petals are red and one whose petals are purple.', 'bare_partition', [add('flower',3,'red'),add('flower',1,'purple')])
case('Build four houses, one whose roof has been painted orange and three white.', 'declared_partition', [add('house',1,'orange'),add('house',3,'white')])
case('Plant blue trees, two small ones and one large one.', 'shared_partition_color', [add('tree',2,'blue'),add('tree',1,'blue')])
case('Add trees, zero purple and four green.', 'partition_negation', [add('tree',4,'green')])
case('Add trees, not one pink and two white.', 'partition_negation', [add('tree',2,'white')])
case('Draw flowers, one blue and one purple near the lake.', 'partition_spatial', [add('flower',1,'blue','near','lake'),add('flower',1,'purple','near','lake')])
case('Create houses, two that are white, three that are yellow, and one pink.', 'bare_partition', [add('house',2,'white'),add('house',3,'yellow'),add('house',1,'pink')])
case('Add three houses, three with pink roofs.', 'declared_partition', [add('house',3,'pink')])
case('Build two houses whose roofs have been painted orange.', 'passive_parts', [add('house',2,'orange')])
case('Place a cottage with a roof which has been coloured purple.', 'passive_parts', [add('house',1,'purple')])
case('Add a home with a roof that had been colored blue.', 'passive_parts', [add('house',1,'blue')])
case('Create a house whose roof has been painted green near the river.', 'passive_spatial', [add('house',1,'green','near','river')])
case('Plant two trees with leaves which have been coloured pink.', 'passive_parts', [add('tree',2,'pink')])
case('Place flowers whose petals have been colored red.', 'passive_parts', [add('flower',1,'red')])
case('Add a house with a roof which had been painted yellow and two with roofs that have been painted white.', 'passive_continuation', [add('house',1,'yellow'),add('house',2,'white')])
case('Add a house with a roof that has been painted white and three blue ones.', 'passive_continuation', [add('house',1,'white'),add('house',3,'blue')])
case('Add rocks, eight total.', 'quantity_total', [add('rock',8)])
case('Build cottages, exactly four total.', 'quantity_total', [add('house',4)])
case('Plant trees, half a dozen total.', 'quantity_total', [add('tree',6)])
case('Create towers, two pairs total.', 'quantity_total', [add('tower',4)])
case('Add flowers, twenty-five total.', 'quantity_total', [add('flower',16)], note='Existing 16-per-action cap applies.')
case('Draw roads, exactly zero total.', 'quantity_total', [])
case('Add bridges, three total over the stream.', 'quantity_total_spatial', [add('bridge',3,relation='across',target='river')])
case('Place mountains, five total behind the castle.', 'quantity_total_spatial', [add('mountain',5,relation='above',target='castle')])
case('Plant one tree that is blue and two pink and three white.', 'omitted_predicates', [add('tree',1,'blue'),add('tree',2,'pink'),add('tree',3,'white')])
case('Build two houses with green roofs and four orange.', 'omitted_predicates', [add('house',2,'green'),add('house',4,'orange')])
case('Add two flowers that are purple and not three pink.', 'omitted_predicates', [add('flower',2,'purple')])
case('Build three small houses and two blue near the pond.', 'omitted_predicate_spatial', [add('house',3,relation='near',target='lake'),add('house',2,'blue','near','lake')])
case('Add two flowers that are yellow and one purple; remove them.', 'group_references', [add('flower',2,'yellow'),add('flower',1,'purple'),remove('flower',3)])
case('Build houses, one blue and one green; put a rock between them.', 'partition_references', [add('house',1,'blue'),add('house',1,'green'),add('rock',relation='between',targets=['house','house'])])
case('Place two cottages, one with a yellow roof and one with an orange roof; remove them.', 'partition_references', [add('house',1,'yellow'),add('house',1,'orange'),remove('house',2)])
case('Plant trees, two green and three pink; remove four of them; remove it.', 'partition_references', [add('tree',2,'green'),add('tree',3,'pink'),remove('tree',4),remove('tree',1)])
case('Keep the lake; add flowers, exactly three total; make it night.', 'quantities_settings', [add('flower',3),setting('time','night')])
case('Behind the tower, plant trees, one blue and two purple.', 'fronted_partition', [add('tree',1,'blue','above','tower'),add('tree',2,'purple','above','tower')])
case('Don’t build a house whose roof has been painted red; add a tree.', 'passive_negation', [add('tree')])
case('Reset; build houses, two with pink roofs and three with white roofs; remove them.', 'partition_reset', [{'action':'reset'},add('house',2,'pink'),add('house',3,'white'),remove('house',5)])

case('Build five houses: two blue and three red.', 'colon_partition', [add('house',2,'blue'),add('house',3,'red')], 'capability_probe')
case('Add flowers, a total of five.', 'quantity_word_order', [add('flower',5)], 'capability_probe')
case('Plant five trees, two green and the remaining three yellow.', 'remainder_partition', [add('tree',2,'green'),add('tree',3,'yellow')], 'capability_probe')
case('Build a house whose roof has already been painted blue.', 'passive_adverb', [add('house',1,'blue')], 'capability_probe')
case('Build five houses, two blue, three red, all near the lake.', 'shared_tail_modifier', [add('house',2,'blue','near','lake'),add('house',3,'red','near','lake')], 'capability_probe')
case('Plant trees, two green, three pink; add two more of the latter.', 'latter_reference', [add('tree',2,'green'),add('tree',3,'pink'),add('tree',2,'pink')], 'capability_probe')
case('Create two groups of three yellow flowers.', 'group_multiplication', [add('flower',6,'yellow')], 'capability_probe')
case('Leave the trees untouched while building two houses.', 'subordinate_creation', [add('house',2)], 'capability_probe')
case('Build a bridge that goes over the stream.', 'finite_relation', [add('bridge',relation='across',target='river')], 'capability_probe')
case('Make it daylight without any snow.', 'setting_paraphrase', [setting('time','day'),setting('weather','clear')], 'capability_probe')


if __name__ == '__main__':
    if DESTINATION.exists():
        raise SystemExit('Refusing to overwrite frozen round-six labels.')
    known, inputs = set(), []
    for name in ['commands.json','heldout_commands.json'] + [f'fresh_commands_v{i}.json' for i in range(2,6)]:
        path = ROOT/'tests'/name
        inputs.append(path)
        data = json.loads(path.read_text(encoding='utf-8'))
        known.update(normalized(c['text']) for c in (data['cases'] if isinstance(data,dict) else data))
    for path in (ROOT/'tests').glob('test_*.py'):
        inputs.append(path)
        known.update(normalized(n.value) for n in ast.walk(ast.parse(path.read_text(encoding='utf-8'))) if isinstance(n,ast.Constant) and isinstance(n.value,str))
    browser, readme = ROOT/'frontend/tests/browser/smoke.spec.js', ROOT/'README.md'
    inputs.extend([browser,readme])
    known.update(normalized(m.group(2)) for m in re.finditer(r"(['\"])([^\n]*?)\1",browser.read_text(encoding='utf-8')))
    known.update(normalized(line) for line in readme.read_text(encoding='utf-8').splitlines())
    texts = [normalized(c['text']) for c in CASES]
    assert len(CASES) == len(set(texts)) == 50
    assert not set(texts)&known, f'Previously used commands: {set(texts)&known}'
    assert sum(c['scope']=='core' for c in CASES) == 40
    pipeline, sources = pipeline_fingerprint()
    dataset = {
        'name':'WordWorld sixth fresh 50-command evaluation — 2026-10-15',
        'method':'50 newly hand-authored commands and expected actions frozen before first prediction after partition/passive/predicate fixes. Author saw implementation and prior errors; not independently human-labeled or randomly sampled. No tuning on round-six predictions.',
        'scope':'40 preassigned core cases and 10 broader probes. Core includes zero/negated groups and a zero-total refusal. Comma partitions replace implicit defaults; declared totals must match group sums. Adjacent and groups remain additions; omitted colors follow the existing noun-type inheritance contract. Trailing locations apply to the groups. Size rendering, geometry and cross-request reference are not scored.',
        'gold_policy':'Exact ordered action dictionaries with aliases and the existing 16-per-action cap. Probe gold represents natural intended English even outside implemented syntax. Each request starts with empty reference state; counted groups feed later bounded removals and two-object spatial references.',
        'parser_sha256_before':hashlib.sha256((ROOT/'backend/parser.py').read_bytes()).hexdigest(),
        'pipeline_sha256_before':pipeline, 'source_files_sha256':sources,
        'uniqueness':'No normalized exact overlaps with all six earlier datasets, Python regression string literals, browser test literals or README lines at freeze time. Similar grammar is intentional; semantic independence is not claimed.',
        'development_inputs_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        'cases':CASES,
    }
    DESTINATION.write_text(json.dumps(dataset,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(f'Frozen {len(CASES)} new commands: {DESTINATION}')
    print(f'Dataset SHA256: {hashlib.sha256(DESTINATION.read_bytes()).hexdigest()}')
    print(f'Parser SHA256: {dataset["parser_sha256_before"]}')
    print(f'Backend pipeline SHA256: {pipeline}')
    print('No parser execution occurred during labeling.')
