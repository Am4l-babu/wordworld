"""Freeze 50 second-round commands and labels without executing the parser."""
import ast
import hashlib
import json
from pathlib import Path
import re

from tests.create_heldout_set import add, remove, setting, normalized

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = Path(__file__).with_name('fresh_commands_v2.json')
CASES = []


def case(text, category, actions, scope='core', note=''):
    CASES.append({'id': f'F{len(CASES)+1:02d}', 'text': text, 'category': category,
                  'scope': scope, 'expected_actions': actions, 'label_note': note})


case('Please don’t plant a forest next to the castle.', 'negation', [])
case('Never erase the bridges or the roads.', 'negation', [])
case('Don‘t build six yellow cabins.', 'negation', [])
case('Keep the pond and add three pink blossoms.', 'protected_mentions', [add('flower', 3, 'pink')])
case('Protect the cottages; delete two rocks.', 'protected_mentions', [remove('rock', 2)])
case('Leave all mountains alone, then show a lighthouse.', 'protected_mentions', [add('tower')])
case('Do not reset the map; insert a road.', 'negation', [add('road')])
case('Don’t add flowers, rocks, or trees; build a blue tower.', 'negation', [add('tower', color='blue')])
case('Retain the forest and remove a bridge.', 'protected_mentions', [remove('bridge', 1)])
case('Avoid the river and create a small castle.', 'protected_mentions', [add('castle')], note='The avoid clause makes no scene changes; the following explicit create clause adds only a castle.')
case('Build thirteen white cottages.', 'quantifiers', [add('house', 13, 'white')])
case('Plant fourteen green trees near the bridge.', 'quantifiers', [add('tree', 14, 'green', 'near', 'bridge')])
case('Add fifteen pink blossoms.', 'quantifiers', [add('flower', 15, 'pink')])
case('Create a dozen red homes beside the path.', 'quantifiers', [add('house', 12, 'red', 'near', 'road')])
case('Put two pairs of rocks west of the pond.', 'quantifiers', [add('rock', 4, relation='left', target='lake')])
case('Grow half a dozen trees behind the fortress.', 'quantifiers', [add('tree', 6, relation='above', target='castle')])
case('Place sixteen orange flowers inside the castle.', 'quantifiers', [add('flower', 16, 'orange', 'inside', 'castle')])
case('Build eighteen huts.', 'quantifiers', [add('house', 16)], note='Apply the documented 16-object per-action cap; a clipping notice should also be present.')
case('Plant three dozen flowers.', 'quantifiers', [add('flower', 16)], note='36 requested objects are clipped to the documented cap of 16.')
case('Add twenty‑two stones.', 'quantifiers', [add('rock', 16)], note='U+2011 nonbreaking hyphen; 22 requested objects are clipped to 16.')
case('North of the bridge, plant three trees.', 'fronted_relations', [add('tree', 3, relation='above', target='bridge')])
case('In front of the tower, place five pink flowers.', 'fronted_relations', [add('flower', 5, 'pink', 'below', 'tower')])
case('Across the stream, build a bridge.', 'fronted_relations', [add('bridge', relation='across', target='river')])
case('Within the fortress, put two rocks.', 'fronted_relations', [add('rock', 2, relation='inside', target='castle')])
case('Between the lake and the mountain, create a road.', 'fronted_relations', [add('road', relation='between', targets=['lake', 'mountain'])])
case('Between two cottages, plant four trees.', 'fronted_relations', [add('tree', 4, relation='between', targets=['house', 'house'])])
case('Close to the castle, build a house and a tower.', 'fronted_relations', [add('house', relation='near', target='castle'), add('tower', relation='near', target='castle')])
case('To the right of the lake place three red cabins.', 'fronted_relations', [add('house', 3, 'red', 'right', 'lake')])
case('Beside the road, do not add any trees.', 'negation', [])
case('Near the lake, build three cottages and two towers.', 'fronted_relations', [add('house', 3, relation='near', target='lake'), add('tower', 2, relation='near', target='lake')])
case('Make it nighttime without snow.', 'settings', [setting('time', 'night'), setting('weather', 'clear')])
case('Make it not snowing.', 'settings', [setting('weather', 'clear')])
case('Stop snowing and make it morning.', 'settings', [setting('weather', 'clear'), setting('time', 'day')])
case('Make it sunny; make it rain; stop the rain.', 'settings', [setting('time', 'day'), setting('weather', 'rain'), setting('weather', 'clear')])
case('Do not make it midnight; make it daylight.', 'setting_paraphrase', [setting('time', 'day')], 'capability_probe', 'Daylight denotes day, but is a new lexical setting paraphrase rather than a documented keyword.')
case('Remove zero towers, then add eleven blue flowers.', 'mixed_actions', [add('flower', 11, 'blue')])
case('Build a house and never remove it.', 'negation', [add('house')], note='Negated removal requires no object resolution or removal action.')
case('Place −2 rocks by the lake.', 'invalid_quantities', [], note='U+2212 minus; negative object counts must not create objects.')
case('Add 1.5 bridges over the river.', 'invalid_quantities', [], note='Fractional counts must be rejected with a notice.')
case('Build two or four cottages.', 'invalid_quantities', [], note='A disjunctive quantity requires clarification rather than guessing one count.')
case('Create a tower and put two trees behind it.', 'coreference', [add('tower'), add('tree', 2, relation='above', target='tower')], 'capability_probe')
case('Plant three flowers and remove one of them.', 'coreference', [add('flower', 3), remove('flower', 1)], 'capability_probe')
case('Build a lake and a castle, then add a road between them.', 'coreference', [add('lake'), add('castle'), add('road', relation='between', targets=['lake', 'castle'])], 'capability_probe')
case('Place two red and three yellow houses.', 'coordination_ellipsis', [add('house', 2, 'red'), add('house', 3, 'yellow')], 'capability_probe')
case('Plant one pink and one purple flower.', 'coordination_ellipsis', [add('flower', 1, 'pink'), add('flower', 1, 'purple')], 'capability_probe')
case('Add a house with a blue roof.', 'postposed_attributes', [add('house', color='blue')], 'capability_probe')
case('Put a bridge spanning the creek.', 'relation_paraphrase', [add('bridge', relation='across', target='river')], 'capability_probe', 'Spanning paraphrases across; creek is an existing landmark, not a requested new river.')
case('Leave the houses untouched while adding a lake.', 'clause_paraphrase', [add('lake')], 'capability_probe', 'The gerund adding introduces a second intended operation after a preservation clause.')
case('To the north of the lake, add a house.', 'fronted_relations', [add('house', relation='above', target='lake')])
case('Construct two red cottages next to the pond.', 'verb_paraphrase', [add('house', 2, 'red', 'near', 'lake')], 'capability_probe', 'Construct is a new creation-verb paraphrase.')


if __name__ == '__main__':
    if DESTINATION.exists():
        raise SystemExit('Refusing to overwrite the frozen second-round dataset.')
    known = set()
    inputs = [ROOT/'tests/commands.json', ROOT/'tests/heldout_commands.json']
    for path in inputs:
        data = json.loads(path.read_text(encoding='utf-8'))
        known.update(normalized(case['text']) for case in (data['cases'] if isinstance(data, dict) else data))
    for path in (ROOT/'tests').glob('test_*.py'):
        inputs.append(path)
        tree = ast.parse(path.read_text(encoding='utf-8'))
        known.update(normalized(node.value) for node in ast.walk(tree) if isinstance(node, ast.Constant) and isinstance(node.value, str))
    browser = ROOT/'frontend/tests/browser/smoke.spec.js'
    readme = ROOT/'README.md'
    inputs.extend([browser, readme])
    known.update(normalized(match.group(2)) for match in re.finditer(r"(['\"])([^\n]*?)\1", browser.read_text(encoding='utf-8')))
    known.update(normalized(line) for line in readme.read_text(encoding='utf-8').splitlines())
    texts = [normalized(case['text']) for case in CASES]
    assert len(CASES) == len(set(texts)) == 50
    assert not set(texts) & known, f'Previously used commands: {set(texts) & known}'
    assert sum(case['scope']=='core' for case in CASES) == 40
    frozen = {
        'name': 'WordWorld second fresh 50-command evaluation — 2026-10-15',
        'method': 'New hand-authored diagnostic commands and gold actions frozen before any parser execution on these inputs, after all priority fixes. Author saw implementation and prior results; not independently human-labeled or randomly sampled. No tuning on second-round predictions.',
        'parser_sha256_before': hashlib.sha256((ROOT/'backend/parser.py').read_bytes()).hexdigest(),
        'scope': '40 core commands and 10 preassigned broader capability probes. All commands are independent and all requested object types are in vocabulary. Reference probes contain their antecedents in the same command. Existing landmarks assumed; scene geometry not scored.',
        'gold_policy': 'Exact ordered action JSON; apply the documented count cap of 16. Invalid/ambiguous counts intentionally produce no action. Labels are immutable after first prediction.',
        'uniqueness': 'No normalized exact overlaps with either previous 50-command set, Python regression strings, browser smoke test strings, or README command lines.',
        'development_inputs_sha256': {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in inputs},
        'cases': CASES,
    }
    DESTINATION.write_text(json.dumps(frozen, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print(f'Frozen {len(CASES)} new commands: {DESTINATION}')
    print(f'Dataset SHA256: {hashlib.sha256(DESTINATION.read_bytes()).hexdigest()}')
    print(f'Parser SHA256: {frozen["parser_sha256_before"]}')
    print('No parser predictions were executed during labeling.')
