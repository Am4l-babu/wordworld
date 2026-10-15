"""Partitions replace implicit defaults and preserve declared totals/references."""
import json
from pathlib import Path

import pytest
from backend.parser import parse
from tests.create_heldout_set import add, remove

cases = json.loads(Path(__file__).with_name('fresh_commands_v5.json').read_text(encoding='utf-8'))['cases']
observed = [c for c in cases if c['id'] in {'J41','J43','J44','J45','J46'}]


@pytest.mark.parametrize('case', observed, ids=[c['id'] for c in observed])
def test_observed_partition_and_attribute_errors(case):
    assert parse(case['text'])['actions'] == case['expected_actions']


@pytest.mark.parametrize('text, expected', [
    ('Add trees, two green and four yellow.', [add('tree',2,'green'),add('tree',4,'yellow')]),
    ('Plant trees, one that is green, two that are blue, and three that are purple.', [add('tree',1,'green'),add('tree',2,'blue'),add('tree',3,'purple')]),
    ('Build five houses, two with blue roofs and three with green roofs.', [add('house',2,'blue'),add('house',3,'green')]),
    ('Build five houses, two blue and three red.', [add('house',2,'blue'),add('house',3,'red')]),
    ('Build houses, five total, two with blue roofs and three with green roofs.', [add('house',2,'blue'),add('house',3,'green')]),
    ('Build two houses, one blue one and one green one.', [add('house',1,'blue'),add('house',1,'green')]),
    ('Build blue houses, one small one and two large ones.', [add('house',1,'blue'),add('house',2,'blue')]),
    ('Plant trees, not two green and three yellow.', [add('tree',3,'yellow')]),
    ('Plant four trees, zero green and four blue.', [add('tree',4,'blue')]),
    ('Add a garden, two pink and one purple.', [add('flower',2,'pink'),add('flower',1,'purple')]),
    ('Add a house and two blue.', [add('house'),add('house',2,'blue')]),
    ('Plant two trees that are green and three yellow and four purple.', [add('tree',2,'green'),add('tree',3,'yellow'),add('tree',4,'purple')]),
    ('Build a cottage whose roof had been colored white.', [add('house',1,'white')]),
    ('Build two houses with roofs which have been painted blue.', [add('house',2,'blue')]),
    ('Place a house with a roof that has been painted pink beside the river.', [add('house',1,'pink','near','river')]),
    ('Add houses, five total near the lake.', [add('house',5,relation='near',target='lake')]),
    ('Add towers, exactly half a dozen total.', [add('tower',6)]),
    ('Add trees, -3 total.', []),
    ('Add flowers, 1.5 total.', []),
    ('Add bridges, zero total.', []),
    ('Add houses, twenty-one total.', [add('house',16)]),
    ('Plant trees, two green and three yellow; remove them.', [add('tree',2,'green'),add('tree',3,'yellow'),remove('tree',5)]),
    ('Near the lake, build houses, two with blue roofs and one with yellow roofs.', [add('house',2,'blue','near','lake'),add('house',1,'yellow','near','lake')]),
    ('Build a house whose roof has been painted blue and two flowers with red petals.', [add('house',1,'blue'),add('flower',2,'red')]),
    ('Build a house near the cottage whose roof has been painted blue and two flowers.', [add('house',relation='near',target='house'),add('flower',2)]),
])
def test_partition_passive_quantity_and_predicate_scope(text, expected):
    assert parse(text)['actions'] == expected


@pytest.mark.parametrize('text', [
    'Build six houses, two with blue roofs and three with green roofs.',
    'Build two houses, one blue and two green.',
    'Build red houses, one blue and one red.',
    'Plant no trees, two green and three yellow.',
    'Plant trees, two green and yellow.',
    'Plant trees, two green and three red or blue.',
    'Build a house whose roof has not been painted blue.',
    'Build a red house whose roof has been painted green.',
    'Add trees, two with blue roofs and one with green roofs.',
    'Add houses, five or six total.',
])
def test_conflicts_and_incomplete_partitions_abstain(text):
    result = parse(text)
    assert result['actions'] == []
    assert result['warnings']


def test_partition_spans_and_bindings_have_no_default_action():
    text = 'Don’t add rocks; plant trees, one green and one blue; put a flower between them; remove it.'
    result = parse(text)
    assert result['actions'] == [add('tree',1,'green'),add('tree',1,'blue'),add('flower',relation='between',targets=['tree','tree']),remove('flower',1)]
    assert result['bindings'] == [{'action_index':2,'target_from':[0,1]},{'action_index':3,'remove_from':[2]}]
    for span in result['tokens'] + result['highlights']:
        assert text[span['start']:span['end']] == span['text']


def test_rules_work_without_spacy(monkeypatch):
    from backend import parser
    monkeypatch.setattr(parser,'NLP',None)
    assert parser.parse('Add houses, two whose roofs have been painted red and three green.')['actions'] == [add('house',2,'red'),add('house',3,'green')]
