"""Post-noun attributes and shared-noun count groups execute without leakage."""
import json
from pathlib import Path

import pytest
from backend.parser import parse
from tests.create_heldout_set import add, remove

HERE = Path(__file__).parent
OBSERVED = []
for filename, ids in [('fresh_commands_v2.json', {'F46'}), ('fresh_commands_v3.json', {'G41','G42','G49','G50'})]:
    OBSERVED.extend(c for c in json.loads((HERE/filename).read_text(encoding='utf-8'))['cases'] if c['id'] in ids)


@pytest.mark.parametrize('case', OBSERVED, ids=[c['id'] for c in OBSERVED])
def test_observed_attribute_failures(case):
    assert parse(case['text'])['actions'] == case['expected_actions']


@pytest.mark.parametrize('text, expected', [
    ('Build two cottages with blue roofs.', [add('house',2,'blue')]),
    ('Add flowers that are purple.', [add('flower',1,'purple')]),
    ('Plant three trees whose leaves are yellow.', [add('tree',3,'yellow')]),
    ('Add a tree with orange foliage and two flowers with pink petals.', [add('tree',1,'orange'),add('flower',2,'pink')]),
    ('Build a house that is green near the blue lake.', [add('house',1,'green','near','lake')]),
    ('Add a house near the green lake and a tree.', [add('house',relation='near',target='lake'),add('tree')]),
    ('Add a tree near the house with blue roofs and a flower.', [add('tree',relation='near',target='house'),add('flower')]),
    ('Add a house with two blue flowers.', [add('house'),add('flower',2,'blue')]),
    ('Add a red house with a red roof.', [add('house',color='red')]),
    ('Build houses, a dozen of them.', [add('house',12)]),
    ('Plant trees, five in total.', [add('tree',5)]),
    ('Add flowers, half a dozen altogether.', [add('flower',6)]),
    ('Build houses, two of them, with white roofs; remove one of them.', [add('house',2,'white'),remove('house',1)]),
    ('Build houses with orange roofs, three of them near the lake.', [add('house',3,'orange','near','lake')]),
    ('Add trees, zero of them; build a cottage.', [add('house')]),
    ('Add trees, -3 of them.', []),
    ('Add flowers, 1.5 of them.', []),
    ('Add rocks, twenty in total.', [add('rock',16)]),
    ('Add two houses, two of them.', [add('house',2)]),
    ('Place two small and four large houses.', [add('house',2),add('house',4)]),
    ('Plant a pair of small and half a dozen large trees.', [add('tree',2),add('tree',6)]),
    ('Place two small, three large, and one tiny house.', [add('house',2),add('house',3),add('house')]),
    ('Place two small and three blue houses.', [add('house',2),add('house',3,'blue')]),
    ('Build two small and not three large cottages.', [add('house',2)]),
    ('Build zero small and one large house.', [add('house')]),
    ('Build one small and one large house; place a tree between them.', [add('house'),add('house'),add('tree',relation='between',targets=['house','house'])]),
    ('Near the lake, place two small and three large houses.', [add('house',2,relation='near',target='lake'),add('house',3,relation='near',target='lake')]),
    ('Build one hundred and two small houses.', [add('house',16)]),
    ('Build two houses with blue roofs and three trees with purple leaves.', [add('house',2,'blue'),add('tree',3,'purple')]),
    ('Build a house with green roofs and red flowers.', [add('house',1,'green'),add('flower',1,'red')]),
    ('Place two small and three large houses with blue roofs.', [add('house',2,'blue'),add('house',3,'blue')]),
    ('Add flowers, twenty-one in total.', [add('flower',16)]),
    ('Build houses, two of them; remove them; remove them.', [add('house',2),remove('house',2)]),
])
def test_scoped_attributes_and_count_groups(text, expected):
    assert parse(text)['actions'] == expected


@pytest.mark.parametrize('text', [
    'Build a red house with a blue roof.',
    'Build two houses, three of them.',
    'Add a house with red and blue roofs.',
    'Add a house whose roof is not blue.',
    'Add a house that is red or blue.',
    'Add a tree with blue roofs.',
    'Build two small and large houses.',
    'Build small and three large houses.',
    'Build two small and three large houses, six of them.',
    'Build houses, two or three of them.',
    'Build houses, many of them.',
    'Build houses, not three of them.',
    'Build houses, two of them, three in total.',
])
def test_ambiguous_or_unsupported_attributes_abstain(text):
    result = parse(text)
    assert result['actions'] == []
    assert result['warnings']


def test_postnoun_annotations_and_reference_bindings_are_exact():
    text = 'Don’t add a tower; build houses, two of them, whose roofs are blue; remove them.'
    result = parse(text)
    assert result['actions'] == [add('house',2,'blue'),remove('house',2)]
    assert result['bindings'] == [{'action_index':1,'remove_from':[0]}]
    assert [h['text'] for h in result['highlights'] if h['role']=='quantity'] == ['two']
    assert [h['text'] for h in result['highlights'] if h['role']=='color'] == ['blue']
    assert [r['text'] for r in result['resolutions']] == ['them']
    for span in result['highlights'] + result['tokens']:
        assert text[span['start']:span['end']] == span['text']


def test_attributes_do_not_require_spacy(monkeypatch):
    from backend import parser
    monkeypatch.setattr(parser,'NLP',None)
    assert parser.parse('Plant trees, three of them, with orange foliage.')['actions'] == [add('tree',3,'orange')]
