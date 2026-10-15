"""Freeze round-three labels and code provenance without parser execution."""
import ast
import hashlib
import json
from pathlib import Path
import re

from tests.create_heldout_set import add, remove, setting, normalized
from tests.evaluate_heldout import pipeline_fingerprint

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = Path(__file__).with_name('fresh_commands_v3.json')
CASES = []


def case(text, category, actions, scope='core', note=''):
    CASES.append({'id': f'G{len(CASES)+1:02d}', 'text': text, 'category': category,
                  'scope': scope, 'expected_actions': actions, 'label_note': note})


case('Add two bridges spanning the stream.', 'relational_roles', [add('bridge', 2, relation='across', target='river')])
case('Place a road crossing the creek.', 'relational_roles', [add('road', relation='across', target='river')])
case('Draw a bridge spanning the river and three red cottages.', 'relational_roles', [add('bridge', relation='across', target='river'), add('house', 3, 'red')])
case('Build a bridge spanning the creek; plant four trees behind it.', 'reference_landmarks', [add('bridge', relation='across', target='river'), add('tree', 4, relation='above', target='bridge')])
case('Don’t build bridges crossing the stream; add a tower.', 'negation', [add('tower')])
case('Create a castle, then put a tree to the left of it.', 'reference_landmarks', [add('castle'), add('tree', relation='left', target='castle')])
case('Build three red cottages; remove two of them.', 'reference_removal', [add('house', 3, 'red'), remove('house', 2)])
case('Plant four flowers; remove one of them; remove them.', 'reference_removal', [add('flower', 4), remove('flower', 1), remove('flower', 3)])
case('Make a tower and a cottage; place a rock between them.', 'reference_landmarks', [add('tower'), add('house'), add('rock', relation='between', targets=['tower','house'])])
case('Add two lakes; put a bridge between them.', 'reference_landmarks', [add('lake', 2), add('bridge', relation='between', targets=['lake','lake'])])
case('Create a road; make it night; plant two trees near it.', 'reference_scope', [add('road'), setting('time','night'), add('tree', 2, relation='near', target='road')])
case('Add a rock; remove it; remove it again.', 'reference_scope', [add('rock'), remove('rock', 1)], note='The second removal has no live antecedent and must abstain, preserving unrelated scene rocks.')
case('Build a house, a tower, and a castle; remove them.', 'reference_removal', [add('house'),add('tower'),add('castle'),remove('house',1),remove('tower',1),remove('castle',1)])
case('Create six trees; erase twenty of them.', 'reference_removal', [add('tree',6),remove('tree',6)], note='Removal is bounded by the six introduced trees, not by unrelated existing trees; a notice is expected.')
case('Add two rocks; never remove them.', 'negation', [add('rock',2)])
case('Build a cottage and a tower; delete one of them.', 'reference_ambiguity', [add('house'),add('tower')], note='A partial selection from a mixed collection is ambiguous; removal abstains with a notice.')
case('Plant three trees; remove it.', 'reference_ambiguity', [add('tree',3)], note='Singular it cannot select one unspecified member of a plural group.')
case('Remove them; add a lake.', 'reference_scope', [add('lake')], note='Every command starts with an empty reference context.')
case('Build a house; reset; put a flower near it.', 'reference_scope', [add('house'),{'action':'reset'}], note='Reset invalidates the house antecedent; the final spatial instruction abstains.')
case('Create one white and one orange house; add a flower between them.', 'coordination_reference', [add('house',color='white'),add('house',color='orange'),add('flower',relation='between',targets=['house','house'])])
case('Add two green and four purple trees.', 'coordination', [add('tree',2,'green'),add('tree',4,'purple')])
case('Build a yellow and a pink cottage.', 'coordination', [add('house',color='yellow'),add('house',color='pink')])
case('Place three white, two blue, and one purple flower.', 'coordination', [add('flower',3,'white'),add('flower',2,'blue'),add('flower',1,'purple')])
case('Plant a pair of yellow and three pink flowers.', 'coordination', [add('flower',2,'yellow'),add('flower',3,'pink')])
case('Build two red and not three blue cottages.', 'coordination_negation', [add('house',2,'red')])
case('Near the tower, plant one pink and one white flower.', 'coordination_spatial', [add('flower',1,'pink','near','tower'),add('flower',1,'white','near','tower')])
case('Add two blue and three red houses behind the lake.', 'coordination_spatial', [add('house',2,'blue','above','lake'),add('house',3,'red','above','lake')])
case('Create one green and one yellow tree; remove them.', 'coordination_reference', [add('tree',1,'green'),add('tree',1,'yellow'),remove('tree',2)])
case('Put one purple and one pink flower beside the castle, then remove it.', 'coordination_reference', [add('flower',1,'purple','near','castle'),add('flower',1,'pink','near','castle'),remove('flower',1)], note='It selects the last singular subject group, the pink flower.')
case('Build two red houses and one blue house; put a rock behind it.', 'reference_landmarks', [add('house',2,'red'),add('house',1,'blue'),add('rock',relation='above',target='house')], note='It refers specifically to the last singular introduction, the blue house.')
case('Keep the lake; add fourteen white flowers.', 'quantity_preservation', [add('flower',14,'white')])
case('Don’t create any castles; build a bridge spanning the stream.', 'negation', [add('bridge',relation='across',target='river')])
case('South of the tower, place a dozen pink flowers.', 'fronted_quantities', [add('flower',12,'pink','below','tower')])
case('Build one hundred and three blue cottages.', 'quantifiers', [add('house',16,'blue')], note='Apply the existing 16-object action cap to 103 requested objects.')
case('Clear everything; add a river; build a bridge spanning it.', 'reference_landmarks', [{'action':'reset'},add('river'),add('bridge',relation='across',target='river')])
case('Make it rain and then stop raining; create a rock.', 'settings', [setting('weather','rain'),setting('weather','clear'),add('rock')])
case('Build zero red and one green house.', 'coordination_negation', [add('house',1,'green')])
case('Add a tree; make it day; remove it.', 'reference_scope', [add('tree'),setting('time','day'),remove('tree',1)])
case('Beside the castle, add a pair of orange flowers and a red house.', 'fronted_quantities', [add('flower',2,'orange','near','castle'),add('house',1,'red','near','castle')])
case('Build a tower; remove it; add two blue flowers.', 'reference_removal', [add('tower'),remove('tower',1),add('flower',2,'blue')])
case('Build a cottage with an orange roof.', 'postposed_attributes', [add('house',color='orange')], 'capability_probe')
case('Place a house whose roof is green.', 'postposed_attributes', [add('house',color='green')], 'capability_probe')
case('Build a bridge that crosses the river.', 'relation_paraphrase', [add('bridge',relation='across',target='river')], 'capability_probe', 'The finite verb crosses paraphrases across; expected output does not request a second river.')
case('Construct three white homes near the river.', 'verb_paraphrase', [add('house',3,'white','near','river')], 'capability_probe')
case('Keep the trees untouched while building a house.', 'clause_paraphrase', [add('house')], 'capability_probe')
case('Make it day without any rain.', 'negated_setting_paraphrase', [setting('time','day'),setting('weather','clear')], 'capability_probe')
case('Add a house to the east side of the lake.', 'direction_paraphrase', [add('house',relation='right',target='lake')], 'capability_probe')
case('Plant two trees and put a flower between those trees.', 'demonstrative_noun_reference', [add('tree',2),add('flower',relation='between',targets=['tree','tree'])], 'capability_probe', 'Those trees names the type explicitly; a correct action match does not establish general demonstrative or color-filtered reference support.')
case('Build houses, three of them.', 'postposed_quantity', [add('house',3)], 'capability_probe')
case('Place two small and three large houses.', 'coordination_without_colors', [add('house',2),add('house',3)], 'capability_probe', 'Score distinct coordinated count groups using existing action fields; size rendering is not scored.')


if __name__ == '__main__':
    if DESTINATION.exists():
        raise SystemExit('Refusing to overwrite frozen round-three labels.')
    known, inputs = set(), []
    for name in ['commands.json','heldout_commands.json','fresh_commands_v2.json']:
        path=ROOT/'tests'/name
        inputs.append(path)
        data=json.loads(path.read_text(encoding='utf-8'))
        known.update(normalized(c['text']) for c in (data['cases'] if isinstance(data,dict) else data))
    for path in (ROOT/'tests').glob('test_*.py'):
        inputs.append(path)
        tree=ast.parse(path.read_text(encoding='utf-8'))
        known.update(normalized(node.value) for node in ast.walk(tree) if isinstance(node,ast.Constant) and isinstance(node.value,str))
    browser=ROOT/'frontend/tests/browser/smoke.spec.js'
    readme=ROOT/'README.md'
    inputs.extend([browser,readme])
    known.update(normalized(m.group(2)) for m in re.finditer(r"(['\"])([^\n]*?)\1",browser.read_text(encoding='utf-8')))
    known.update(normalized(line) for line in readme.read_text(encoding='utf-8').splitlines())
    texts=[normalized(c['text']) for c in CASES]
    assert len(CASES)==len(set(texts))==50
    assert not set(texts)&known, f'Previously used commands: {set(texts)&known}'
    assert sum(c['scope']=='core' for c in CASES)==40
    pipeline, sources=pipeline_fingerprint()
    dataset={
        'name':'WordWorld third fresh 50-command evaluation — 2026-10-15',
        'method':'50 newly hand-authored commands and expected actions frozen before prediction after reference/coordination fixes. Author saw implementation and prior results; not independently human-labeled or randomly sampled. No tuning on round-three results.',
        'scope':'40 core commands and 10 preassigned broader grammar probes. All commands start with empty request-local reference context. Singular it resolves the latest live singular introduction; them resolves the latest coordinated creation collection. Explicit new creation verbs reset collection focus. Existing named landmarks assumed; geometry and cross-request context are not scored.',
        'gold_policy':'Exact ordered action dictionaries; existing aliases/count cap apply. Missing or ambiguous antecedents and repeated removals from exhausted references intentionally abstain. Refusal cases measure the documented conservative contract, not general English understanding.',
        'parser_sha256_before':hashlib.sha256((ROOT/'backend/parser.py').read_bytes()).hexdigest(),
        'pipeline_sha256_before':pipeline,
        'source_files_sha256':sources,
        'uniqueness':'No normalized exact overlaps with all three previous sets, Python regression string literals, browser smoke-test string literals, or README command lines. Similar grammar constructions are intentional.',
        'development_inputs_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        'cases':CASES,
    }
    DESTINATION.write_text(json.dumps(dataset,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(f'Frozen {len(CASES)} new commands: {DESTINATION}')
    print(f'Dataset SHA256: {hashlib.sha256(DESTINATION.read_bytes()).hexdigest()}')
    print(f'Parser SHA256: {dataset["parser_sha256_before"]}')
    print(f'Backend pipeline SHA256: {pipeline}')
    print('No parser execution occurred during labeling.')
