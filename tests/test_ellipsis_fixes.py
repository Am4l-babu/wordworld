"""Observed round-four failures and compositional quantity/ellipsis regressions."""
import json
from pathlib import Path

import pytest
from backend.parser import parse
from tests.create_heldout_set import add, remove

cases = json.loads(Path(__file__).with_name('fresh_commands_v4.json').read_text(encoding='utf-8'))['cases']
observed = [c for c in cases if c['id'] in {'H41','H42','H43','H44','H46','H47'}]


@pytest.mark.parametrize('case', observed, ids=[c['id'] for c in observed])
def test_observed_failures(case):
    assert parse(case['text'])['actions'] == case['expected_actions']


@pytest.mark.parametrize('text, expected', [
    ('Plant exactly five trees.', [add('tree',5)]),
    ('Exactly five flowers.', [add('flower',5)]),
    ('Add houses, exactly a dozen of them.', [add('house',12)]),
    ('Add rocks, exactly seven in all.', [add('rock',7)]),
    ('Build houses with red roofs, exactly five in all.', [add('house',5,'red')]),
    ('Add flowers, exactly 1.5 of them.', []),
    ('Add flowers, exactly -5 in all.', []),
    ('Add flowers, exactly zero in all.', []),
    ('Build two houses with a roof painted purple.', [add('house',2,'purple')]),
    ('Build cottages whose roofs are painted white.', [add('house',1,'white')]),
    ('Place a cottage with a roof which is green near the lake.', [add('house',1,'green','near','lake')]),
    ('Build a cottage that has a blue roof and a house with roofs colored orange.', [add('house',1,'blue'),add('house',1,'orange')]),
    ('Plant two trees with leaves coloured yellow.', [add('tree',2,'yellow')]),
    ('Build two red houses and three blue ones.', [add('house',2,'red'),add('house',3,'blue')]),
    ('Build a red house and a blue one.', [add('house',1,'red'),add('house',1,'blue')]),
    ('Build two houses, three large ones, and one tiny one.', [add('house',2),add('house',3),add('house')]),
    ('Plant two trees and exactly three large ones with purple leaves.', [add('tree',2),add('tree',3,'purple')]),
    ('Build two cottages and not three large ones.', [add('house',2)]),
    ('Build one house and zero large ones.', [add('house')]),
    ('Add a cottage and two trees and three large ones.', [add('house'),add('tree',2),add('tree',3)]),
    ('Place two small houses and three large ones near the river.', [add('house',2,relation='near',target='river'),add('house',3,relation='near',target='river')]),
    ('Grow two trees that are purple and four that are white.', [add('tree',2,'purple'),add('tree',4,'white')]),
    ('Add two houses with blue roofs and three whose roofs are red.', [add('house',2,'blue'),add('house',3,'red')]),
    ('Place two flowers that are pink, three which are white, and one that is purple.', [add('flower',2,'pink'),add('flower',3,'white'),add('flower',1,'purple')]),
    ('Plant two trees that are green and not three that are yellow.', [add('tree',2,'green')]),
    ('Build one house whose roof is blue and one whose roof is yellow; place a tree between them.', [add('house',1,'blue'),add('house',1,'yellow'),add('tree',relation='between',targets=['house','house'])]),
    ('Build two houses and three blue ones; remove them.', [add('house',2),add('house',3,'blue'),remove('house',5)]),
    ('Plant flowers, exactly five in all; remove three of them; remove them.', [add('flower',5),remove('flower',3),remove('flower',2)]),
    ('Build two houses with blue roofs and three trees that are purple.', [add('house',2,'blue'),add('tree',3,'purple')]),
    ('Build two small and three large houses and four blue ones.', [add('house',2),add('house',3),add('house',4,'blue')]),
    ('Build zero houses and three blue ones.', [add('house',3,'blue')]),
    ('Build no houses and two green ones.', [add('house',2,'green')]),
    ('Build a house and one hundred and one blue ones.', [add('house'),add('house',16,'blue')]),
    ('Build a house and twenty-one blue ones.', [add('house'),add('house',16,'blue')]),
])
def test_quantity_roof_and_inherited_groups(text, expected):
    assert parse(text)['actions'] == expected


@pytest.mark.parametrize('text', [
    'Add flowers, exactly a few of them.',
    'Build a house with a roof that is not blue.',
    'Build a red house with a roof painted blue.',
    'Build houses with roofs painted red or blue.',
    'Build two houses and large ones.',
    'Build two houses and two or three large ones.',
    'Build two houses and -3 large ones.',
    'Plant two trees that are green and three that are red or blue.',
    'Plant two trees that are green and three that are near the lake.',
    'Add flowers, exactly five and three in all.',
    'Build two houses and three small and four large ones.',
])
def test_ambiguity_and_unsupported_groups_abstain(text):
    result = parse(text)
    assert result['actions'] == []
    assert result['warnings']


def test_exact_spans_and_bindings_for_inherited_groups():
    text = 'Don’t add rocks; build a house with a roof painted blue and one yellow one; put a tree between them.'
    result = parse(text)
    assert result['actions'] == [add('house',1,'blue'),add('house',1,'yellow'),add('tree',relation='between',targets=['house','house'])]
    assert result['bindings'] == [{'action_index':2,'target_from':[0,1]}]
    for span in result['tokens'] + result['highlights']:
        assert text[span['start']:span['end']] == span['text']
    assert [h['text'] for h in result['highlights'] if h['role']=='color'] == ['blue','yellow']


def test_unresolved_ellipsis_is_reported_and_never_crosses_requests():
    parse('Build a house.')
    result = parse('Add three large ones.')
    assert not result['actions']
    assert result['warnings']


def test_ellipsis_does_not_inherit_a_landmark_type():
    result = parse('Build two houses near the lake and three large ones.')
    assert result['actions'] == [add('house',2,relation='near',target='lake')]
    assert result['warnings']


@pytest.mark.parametrize('text', [
    'Build two houses near the lake and three large ones behind the castle.',
    'Build two houses; add three large ones behind the castle.',
])
def test_unsupported_ellipsis_never_creates_its_landmark(text):
    result = parse(text)
    assert not any(a.get('type') == 'castle' for a in result['actions'])
    assert result['warnings']


def test_new_rules_do_not_require_spacy(monkeypatch):
    from backend import parser
    monkeypatch.setattr(parser,'NLP',None)
    assert parser.parse('Build two houses that are blue and three that are red.')['actions'] == [add('house',2,'blue'),add('house',3,'red')]
