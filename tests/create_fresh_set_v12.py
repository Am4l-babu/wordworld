"""Freeze twelfth-round gold (place filters, filtered removal, fractions, 'each' wordings) before any parser run on it."""
import ast
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote
from tests.create_heldout_set import add, remove, setting, normalized
from tests.evaluate_heldout import pipeline_fingerprint

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = Path(__file__).with_name('fresh_commands_v12.json')
CASES = []


def where(action, relation=None, target=None):
    """Attach a place filter ("the trees near the lake") to an action."""
    if relation:
        action.update(filter_relation=relation, filter_target=target)
    return action


def recolor(kind, count, color, filter_color=None, relation=None, target=None):
    action = {'action': 'recolor', 'type': kind, 'count': count, 'color': color}
    if filter_color:
        action['filter_color'] = filter_color
    return where(action, relation, target)


def resize(kind, count, scale, relation=None, target=None):
    return where({'action': 'resize', 'type': kind, 'count': count, 'scale': scale}, relation, target)


def move(kind, count, relation, target, filter_relation=None, filter_target=None):
    return where({'action': 'move', 'type': kind, 'count': count, 'relation': relation, 'target': target}, filter_relation, filter_target)


def drop(kind, count, relation=None, target=None):
    return where({'action': 'remove', 'type': kind, 'count': count}, relation, target)


def case(text, category, actions, scope='core', context=None, note=''):
    item = {'id': f'S{len(CASES) + 1:02d}', 'text': text, 'category': category, 'scope': scope, 'expected_actions': actions, 'label_note': note}
    if context:
        item['context'] = context
    CASES.append(item)


# Recolor and resize with a place filter
case('Paint the flowers near the road white.', 'filter_recolor', [recolor('flower', 'all', 'white', relation='near', target='road')])
case('Make the trees behind the castle taller.', 'filter_resize', [resize('tree', 'all', 1.25, 'above', 'castle')])
case('Shrink the rocks to the right of the river.', 'filter_resize', [resize('rock', 'all', 0.8, 'right', 'river')])
case('Dye the houses in front of the lake orange.', 'filter_recolor', [recolor('house', 'all', 'orange', relation='below', target='lake')])
case('Colour the red flowers beside the lake pink.', 'filter_with_color_filter', [recolor('flower', 'all', 'pink', 'red', 'near', 'lake')])
case('Paint the trees inside the lake green.', 'filter_inside', [recolor('tree', 'all', 'green', relation='inside', target='lake')])
case('Make the houses near the lake red.', 'filter_make_recolor', [recolor('house', 'all', 'red', relation='near', target='lake')])
case('Make the flowers by the road yellow.', 'filter_by', [recolor('flower', 'all', 'yellow', relation='near', target='road')])
case('Paint the trees close to the lake blue.', 'filter_close_to', [recolor('tree', 'all', 'blue', relation='near', target='lake')])
case('Make the castle near the lake smaller.', 'filter_singular', [resize('castle', 1, 0.8, 'near', 'lake')])
case('Make the towers near the castle smaller.', 'filter_resize', [resize('tower', 'all', 0.8, 'near', 'castle')])
case('Enlarge the towers behind the houses a lot.', 'filter_amount', [resize('tower', 'all', 1.5, 'above', 'house')])
# Filtered removal
case('Remove the flowers next to the house.', 'filter_remove', [drop('flower', 'all', 'near', 'house')])
case('Delete one tree behind the castle.', 'filter_remove_count', [drop('tree', 1, 'above', 'castle')])
case('Erase the rocks left of the lake.', 'filter_remove', [drop('rock', 'all', 'left', 'lake')])
case('Get rid of three trees near the river.', 'filter_remove_count', [drop('tree', 3, 'near', 'river')])
case('Destroy all the houses in front of the mountain.', 'filter_remove_all', [drop('house', 'all', 'below', 'mountain')])
case('Remove every flower beside the road.', 'filter_remove_every', [drop('flower', 'all', 'near', 'road')])
# Moves with a filter and a destination
case('Move the flowers near the lake to the left of the castle.', 'filter_move', [move('flower', 'all', 'left', 'castle', 'near', 'lake')])
case('Move the trees right of the house behind the lake.', 'filter_move', [move('tree', 'all', 'above', 'lake', 'right', 'house')])
case('Shift the rocks near the road next to the tower.', 'filter_move', [move('rock', 'all', 'near', 'tower', 'near', 'road')])
case('Move the flowers near the lake.', 'move_destination_not_filter', [{'action': 'move', 'type': 'flower', 'count': 'all', 'relation': 'near', 'target': 'lake'}])
# Coordination and sequencing
case('Make the houses near the river bigger and paint the trees near the lake purple.', 'filter_coordinated', [resize('house', 'all', 1.25, 'near', 'river'), recolor('tree', 'all', 'purple', relation='near', target='lake')])
case('Paint the flowers near the lake red, the flowers near the road white.', 'filter_comma_continuation', [recolor('flower', 'all', 'red', relation='near', target='lake'), recolor('flower', 'all', 'white', relation='near', target='road')])
case('Make it night and remove the trees near the lake.', 'setting_then_filter', [setting('time', 'night'), drop('tree', 'all', 'near', 'lake')])
case('Remove the trees near the lake and add two flowers near the lake.', 'filter_remove_then_add', [drop('tree', 'all', 'near', 'lake'), add('flower', 2, None, 'near', 'lake')])
case('Remove the rocks near the lake, then plant a tree.', 'filter_remove_then_add', [drop('rock', 'all', 'near', 'lake'), add('tree')])
# Creation wording that must not be read as a filter
case('Plant two trees near the lake.', 'creation_not_filter', [add('tree', 2, None, 'near', 'lake')])
case('Put three flowers behind the castle.', 'creation_not_filter', [add('flower', 3, None, 'above', 'castle')])
case('Delete two cottages.', 'unfiltered_remove', [drop('house', 2)])
# Refusals
case("Don't remove the trees near the lake.", 'filter_negated', [])
case('Remove the trees between the houses.', 'filter_unsupported_between', [])
case('Paint the trees between the lake and the castle red.', 'filter_unsupported_between', [])
case('Remove the trees near it.', 'filter_pronoun_landmark', [])
case('Resize the mountains near the river.', 'filter_missing_value', [])
case('Paint the trees near the lake.', 'filter_missing_color', [])
# Fractions and a context reference
case('Plant twenty trees: 15% pink, 35% white and the rest green.', 'percent_remainder', [add('tree', 3, 'pink'), add('tree', 7, 'white'), add('tree', 10, 'green')])
case('Build nine houses: a third red, a third blue and a third green.', 'thirds_triple', [add('house', 3, 'red'), add('house', 3, 'blue'), add('house', 3, 'green')])
case('Create twenty flowers: one tenth pink and nine tenths white.', 'tenths', [add('flower', 2, 'pink'), add('flower', 18, 'white')])
case('Paint them red.', 'context_recolor', [recolor('tree', 3, 'red')], context=[{'type': 'tree', 'count': 3}])
# Broader probes: intended natural English, including forms outside the grammar
case('Paint the trees red near the lake.', 'filter_after_value', [recolor('tree', 'all', 'red', relation='near', target='lake')], 'capability_probe')
case('Remove the trees that are near the lake.', 'filter_relative_clause', [drop('tree', 'all', 'near', 'lake')], 'capability_probe')
case('Remove the trees on the left of the lake.', 'filter_on_the_left', [drop('tree', 'all', 'left', 'lake')], 'capability_probe')
case('Plant trees in each of pink and white, two per color.', 'each_in_each_of', [add('tree', 2, 'pink'), add('tree', 2, 'white')], 'capability_probe')
case('Place a pair of flowers in each of red and yellow.', 'each_pair_in_each_of', [add('flower', 2, 'red'), add('flower', 2, 'yellow')], 'capability_probe')
case('Add flowers in pink and white, four of each.', 'each_trailing_count', [add('flower', 4, 'pink'), add('flower', 4, 'white')], 'capability_probe')
case('Plant ten trees: three pink; the rest green.', 'semicolon_remainder', [add('tree', 3, 'pink'), add('tree', 7, 'green')], 'capability_probe')
case('Draw two clusters of three flowers.', 'group_multiplication', [add('flower', 6)], 'capability_probe')
case('Build three houses, then make two of them red.', 'create_then_partial_reference', [add('house', 3), recolor('house', 2, 'red')], 'capability_probe')
case('Build twelve houses: a sixth red and the rest blue.', 'sixths', [add('house', 2, 'red'), add('house', 10, 'blue')], 'capability_probe')


if __name__ == '__main__':
    if DESTINATION.exists():
        raise SystemExit('Refusing to overwrite frozen round-twelve labels.')
    known, inputs = set(), []
    for name in ['commands.json', 'heldout_commands.json'] + [f'fresh_commands_v{i}.json' for i in range(2, 12)]:
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
    assert len(CASES) == len(set(texts)) == 50, len(CASES)
    assert not set(texts) & known, f'Previously used commands: {set(texts) & known}'
    assert sum(c['scope'] == 'core' for c in CASES) == 40, sum(c['scope'] == 'core' for c in CASES)
    pipeline, sources = pipeline_fingerprint()
    dataset = {
        'name': 'WordWorld twelfth fresh 50-command evaluation — 2026-10-18',
        'method': '50 newly hand-authored commands and expected actions frozen before first prediction. The place-filter grammar for edits '
                  'and removals was already implemented, so these commands test it on unseen sentences, not on the sentences used to build it. '
                  'The author wrote the grammar and saw prior errors; not independent.',
        'scope': '40 preassigned core cases (place filters on recolor/resize/remove/move, filter vs destination, coordination, creation wording '
                 'that must not become a filter, negation and refusals, thirds/tenths/percentages, one context reference) and 10 broader probes '
                 '(filter wordings, alternate "each" wordings, group multiplication, sixths, partial references).',
        'gold_policy': "Exact ordered action dictionaries. Place filters add filter_relation/filter_target; scale factors follow the documented edit "
                       'semantics. Probe gold represents intended natural English, including forms outside the grammar.',
        'parser_sha256_before': hashlib.sha256((ROOT / 'backend/parser.py').read_bytes()).hexdigest(),
        'pipeline_sha256_before': pipeline, 'source_files_sha256': sources,
        'uniqueness': 'No normalized exact overlaps with all twelve earlier datasets, Python test literals, browser/scene test and UI '
                      'example literals, README/archive lines or decoded command links at freeze time.',
        'development_inputs_sha256': {str(p.relative_to(ROOT)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        'cases': CASES,
    }
    DESTINATION.write_text(json.dumps(dataset, indent=2, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')
    print('Frozen 50 new commands; no parser execution occurred during labeling.')
    print('Dataset SHA256:', hashlib.sha256(DESTINATION.read_bytes()).hexdigest())
    print('Backend pipeline SHA256:', pipeline)
