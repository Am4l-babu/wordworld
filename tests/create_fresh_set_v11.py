"""Freeze eleventh-round gold (edits, cross-request references, fractions) before any parser run on it."""
import ast
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote
from tests.create_heldout_set import add, remove, setting, normalized
from tests.evaluate_heldout import pipeline_fingerprint

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = Path(__file__).with_name('fresh_commands_v11.json')
CASES = []


def recolor(kind, count, color, filter_color=None):
    action = {'action': 'recolor', 'type': kind, 'count': count, 'color': color}
    if filter_color:
        action['filter_color'] = filter_color
    return action


def resize(kind, count, scale):
    return {'action': 'resize', 'type': kind, 'count': count, 'scale': scale}


def move(kind, count, relation=None, target=None, targets=None, direction=None, distance='medium'):
    action = {'action': 'move', 'type': kind, 'count': count}
    if relation:
        action.update(relation=relation, target=target or targets[0])
        if targets:
            action['targets'] = targets
    else:
        action.update(direction=direction, distance=distance)
    return action


def case(text, category, actions, scope='core', context=None, note=''):
    item = {'id': f'R{len(CASES) + 1:02d}', 'text': text, 'category': category, 'scope': scope, 'expected_actions': actions, 'label_note': note}
    if context:
        item['context'] = context
    CASES.append(item)


HOUSE, TREES3, CASTLE = [{'type': 'house', 'count': 1}], [{'type': 'tree', 'count': 3}], [{'type': 'castle', 'count': 1}]

# Recolor
case('Paint the cottage pink.', 'recolor', [recolor('house', 1, 'pink')])
case('Colour all the flowers orange.', 'recolor_all', [recolor('flower', 'all', 'orange')])
case('Make the woods purple.', 'recolor_collective', [recolor('tree', 'all', 'purple')])
case('Dye the yellow flowers blue.', 'recolor_filtered', [recolor('flower', 'all', 'blue', 'yellow')])
case('Change the colour of the homes to green.', 'recolor_change_of', [recolor('house', 'all', 'green')])
case('Change the house to orange.', 'recolor_change_to', [recolor('house', 1, 'orange')])
case('Paint the castle red.', 'recolor_unmapped', [], note='Castles have no color mapping; a notice, no action.')
case("Don't paint the trees white.", 'recolor_negated', [])
# Resize
case('Make the lake bigger.', 'resize', [resize('lake', 1, 1.25)])
case('Make all the rocks much smaller.', 'resize_amount', [resize('rock', 'all', 0.67)])
case('Enlarge the tower slightly.', 'resize_verb_amount', [resize('tower', 1, 1.12)])
case('Shrink the mountains.', 'resize_verb', [resize('mountain', 'all', 0.8)])
case('Make the bridge a little larger.', 'resize_amount', [resize('bridge', 1, 1.12)])
case('Resize the castle.', 'resize_missing_value', [])
# Move to a landmark
case('Move the castle next to the river.', 'move_relation', [move('castle', 1, 'near', 'river')])
case('Move the flowers in front of the cottage.', 'move_relation', [move('flower', 'all', 'below', 'house')])
case('Relocate the tower to the right of the mountain.', 'move_relation', [move('tower', 1, 'right', 'mountain')])
case('Shift the rock between the lake and the road.', 'move_between', [move('rock', 1, 'between', targets=['lake', 'road'])])
case('Move two of the trees behind the castle.', 'move_partial', [move('tree', 2, 'above', 'castle')])
case('Move the bridge across the river.', 'move_across', [move('bridge', 1, 'across', 'river')])
# Move by direction
case('Move the house to the left.', 'move_direction', [move('house', 1, direction='left')])
case('Slide the castle a bit to the right.', 'move_direction_amount', [move('castle', 1, direction='right', distance='small')])
case('Shift the trees far back.', 'move_direction_amount', [move('tree', 'all', direction='up', distance='large')])
case('Move the lake forward.', 'move_direction', [move('lake', 1, direction='down')])
# Coordinated and sequenced edits
case('Paint the houses red and the flowers white.', 'coordinated_edit', [recolor('house', 'all', 'red'), recolor('flower', 'all', 'white')])
case('Make the castle bigger and move it behind the lake.', 'edit_chain_reference', [resize('castle', 1, 1.25), move('castle', 1, 'above', 'lake')])
case('Build two towers, then make them smaller.', 'create_then_edit', [add('tower', 2), resize('tower', 2, 0.8)])
case('Plant a tree and paint it orange.', 'create_then_edit', [add('tree'), recolor('tree', 1, 'orange')])
# Cross-request references (context = what the previous command touched)
case('Make it purple.', 'context_recolor', [recolor('house', 1, 'purple')], context=HOUSE)
case('Move them to the left of the lake.', 'context_move', [move('tree', 3, 'left', 'lake')], context=TREES3)
case('Make them much bigger.', 'context_mixed_resize', [resize('house', 2, 1.5), resize('tree', 1, 1.5)], context=[{'type': 'house', 'count': 2}, {'type': 'tree', 'count': 1}])
case('Get rid of it.', 'context_remove', [remove('castle', 1)], context=CASTLE)
case('Put two flowers next to it.', 'context_landmark', [add('flower', 2, None, 'near', 'castle')], context=CASTLE)
case('Paint it white.', 'context_agreement', [], context=[{'type': 'flower', 'count': 4}], note="'it' cannot name four flowers.")
case('Plant a tree and make it pink.', 'context_local_first', [add('tree'), recolor('tree', 1, 'pink')], context=HOUSE)
# Fractions of a declared total
case('Plant fifteen trees: a third pink and the rest green.', 'thirds', [add('tree', 5, 'pink'), add('tree', 10, 'green')])
case('Create ten flowers: 40% white and 60% yellow.', 'percentages', [add('flower', 4, 'white'), add('flower', 6, 'yellow')])
case('Build six houses: two thirds blue and one third red.', 'thirds', [add('house', 4, 'blue'), add('house', 2, 'red')])
case('Plant five trees: one fifth orange and four fifths green.', 'fifths', [add('tree', 1, 'orange'), add('tree', 4, 'green')])
case('Build seven houses: a third blue and the rest red.', 'nonintegral_thirds', [])
# Broader probes: intended natural English, including forms outside the grammar
case('Turn the two blue houses white.', 'recolor_counted_filter', [recolor('house', 2, 'white', 'blue')], 'capability_probe')
case('Give the cottage a red roof.', 'recolor_give', [recolor('house', 1, 'red')], 'capability_probe')
case('Move the castle closer to the lake.', 'move_closer', [move('castle', 1, 'near', 'lake')], 'capability_probe')
case('Make both houses green.', 'recolor_both', [recolor('house', 2, 'green')], 'capability_probe')
case('Make the houses a bit taller.', 'resize_taller', [resize('house', 'all', 1.12)], 'capability_probe')
case('Move the castle up a little.', 'move_trailing_amount', [move('castle', 1, direction='up', distance='small')], 'capability_probe')
case('Make it night and paint the houses blue.', 'setting_then_edit', [setting('time', 'night'), recolor('house', 'all', 'blue')], 'capability_probe')
case('Recolor every cottage in purple.', 'recolor_every_in', [recolor('house', 'all', 'purple')], 'capability_probe')
case('Plant twelve flowers: 25 per cent pink, a quarter white and the rest yellow.', 'mixed_percent_fraction', [add('flower', 3, 'pink'), add('flower', 3, 'white'), add('flower', 6, 'yellow')], 'capability_probe')
case('Make them yellow and move them next to the road.', 'context_edit_chain', [recolor('flower', 2, 'yellow'), move('flower', 2, 'near', 'road')], 'capability_probe', context=[{'type': 'flower', 'count': 2}])


if __name__ == '__main__':
    if DESTINATION.exists():
        raise SystemExit('Refusing to overwrite frozen round-eleven labels.')
    known, inputs = set(), []
    for name in ['commands.json', 'heldout_commands.json'] + [f'fresh_commands_v{i}.json' for i in range(2, 11)]:
        path = ROOT / 'tests' / name
        inputs.append(path)
        data = json.loads(path.read_text(encoding='utf-8'))
        known.update(normalized(c['text']) for c in (data['cases'] if isinstance(data, dict) else data))
    for path in (ROOT / 'tests').glob('test_*.py'):
        inputs.append(path)
        known.update(normalized(n.value) for n in ast.walk(ast.parse(path.read_text(encoding='utf-8'))) if isinstance(n, ast.Constant) and isinstance(n.value, str))
    for path in [*(ROOT / 'frontend/tests/browser').glob('*.spec.js'), ROOT / 'frontend/tests/world.test.js', ROOT / 'frontend/scripts/capture-readme.mjs',
                 ROOT / 'frontend/src/world.js', ROOT / 'frontend/src/App.jsx', ROOT / 'frontend/src/components/HelpDialog.jsx',
                 ROOT / 'README.md', ROOT / 'docs/DEVELOPMENT.md']:
        inputs.append(path)
        content = path.read_text(encoding='utf-8-sig')
        known.update(normalized(m.group(2)) for m in re.finditer(r"(['\"])([^\n]*?)\1", content))
        known.update(normalized(line) for line in content.splitlines())
        known.update(normalized(unquote(s)) for s in re.findall(r'[?&]command=([^\s)"<>]+)', content))
    texts = [normalized(c['text']) for c in CASES]
    assert len(CASES) == len(set(texts)) == 50
    assert not set(texts) & known, f'Previously used commands: {set(texts) & known}'
    assert sum(c['scope'] == 'core' for c in CASES) == 40
    pipeline, sources = pipeline_fingerprint()
    dataset = {
        'name': 'WordWorld eleventh fresh 50-command evaluation — 2026-10-16',
        'method': '50 newly hand-authored commands and expected actions frozen before first prediction, after adding language edits '
                  '(recolor/resize/move), cross-request references and thirds/fifths/percentages. The author wrote the grammar and saw '
                  'prior errors; not independent.',
        'scope': '40 preassigned core cases (edits, landmarks, directions, chains, references with client context, fractions, negation, '
                 'unmapped colors, missing values, agreement and non-integral fractions) and 10 broader probes.',
        'gold_policy': "Exact ordered action dictionaries. A case's optional context lists what the previous command touched, oldest "
                       'first, as the client sends it. Scale factors follow the documented edit semantics (bigger 1.25, much 1.5, a bit 1.12; '
                       'smaller 0.8, much 0.67, a bit 0.89). Probe gold represents intended natural English, including forms outside the grammar.',
        'parser_sha256_before': hashlib.sha256((ROOT / 'backend/parser.py').read_bytes()).hexdigest(),
        'pipeline_sha256_before': pipeline, 'source_files_sha256': sources,
        'uniqueness': 'No normalized exact overlaps with all eleven earlier datasets, Python test literals, browser/scene test and UI '
                      'example literals, README/archive lines or decoded command links at freeze time.',
        'development_inputs_sha256': {str(p.relative_to(ROOT)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        'cases': CASES,
    }
    DESTINATION.write_text(json.dumps(dataset, indent=2, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')
    print('Frozen 50 new commands; no parser execution occurred during labeling.')
    print('Dataset SHA256:', hashlib.sha256(DESTINATION.read_bytes()).hexdigest())
    print('Backend pipeline SHA256:', pipeline)
