"""Rational quarter partitions, of-each-color lists and clause-scoped locations."""
import json
from pathlib import Path
import pytest
from backend.parser import parse
from tests.create_heldout_set import add,remove

observed=[c for c in json.loads(Path(__file__).with_name('fresh_commands_v9.json').read_text(encoding='utf-8'))['cases'] if c['id'] in {'P42','P49','P50','P47'}]


@pytest.mark.parametrize('case',observed,ids=[c['id'] for c in observed])
def test_observed_errors(case):
    assert parse(case['text'])['actions']==case['expected_actions']


@pytest.mark.parametrize('text,expected',[
    ('Plant eight trees: a quarter blue and three quarters green.',[add('tree',2,'blue'),add('tree',6,'green')]),
    ('Build twelve houses: one quarter pink and three-quarters white.',[add('house',3,'pink'),add('house',9,'white')]),
    ('Add four flowers: quarter yellow and three quarters purple.',[add('flower',1,'yellow'),add('flower',3,'purple')]),
    ('Plant eight trees: two quarters red and half blue.',[add('tree',4,'red'),add('tree',4,'blue')]),
    ('Build eight houses: one quarter blue, one quarter red, and half white.',[add('house',2,'blue'),add('house',2,'red'),add('house',4,'white')]),
    ('Build eight houses: one quarter with blue roofs and three quarters whose roofs are green.',[add('house',2,'blue'),add('house',6,'green')]),
    ('Place four flowers: one quarter of them red and three quarters of them white.',[add('flower',1,'red'),add('flower',3,'white')]),
    ('Plant eight trees: one quarter purple and the rest yellow.',[add('tree',2,'purple'),add('tree',6,'yellow')]),
    ('Add eight flowers: 1 quarter orange and 3 quarters blue.',[add('flower',2,'orange'),add('flower',6,'blue')]),
    ('Build four blue houses: four quarters large ones.',[add('house',4,'blue')]),
    ('Plant zero trees: one quarter green and three quarters white.',[]),
    ('Build eighty houses: one quarter yellow and three quarters orange.',[add('house',16,'yellow'),add('house',16,'orange')]),
    ('Create two flowers of each color: pink and blue.',[add('flower',2,'pink'),add('flower',2,'blue')]),
    ('Build a house of each colour: red and yellow.',[add('house',1,'red'),add('house',1,'yellow')]),
    ('Plant trees of each color: red and blue.',[]),
    ('Add half a dozen flowers of each colour: white and purple.',[add('flower',6,'white'),add('flower',6,'purple')]),
    ('Plant two trees of each color, green, blue, and pink.',[add('tree',2,'green'),add('tree',2,'blue'),add('tree',2,'pink')]),
    ('Add zero flowers of each color: red and white.',[]),
    ('Add twenty flowers of each color: pink and orange.',[add('flower',16,'pink'),add('flower',16,'orange')]),
    ('Build two houses of each color: white and purple near the lake.',[add('house',2,'white','near','lake'),add('house',2,'purple','near','lake')]),
    ('Build a house and two trees, all near the river.',[add('house',relation='near',target='river'),add('tree',2,relation='near',target='river')]),
    ('Create two pink flowers and one blue cottage, all left of the lake.',[add('flower',2,'pink','left','lake'),add('house',1,'blue','left','lake')]),
    ('Add a castle and a tower, all between the house and the pond.',[add('castle',relation='between',targets=['house','lake']),add('tower',relation='between',targets=['house','lake'])]),
    ('Build four houses: one quarter blue and three quarters white and two green trees, all behind the lake.',[add('house',1,'blue','above','lake'),add('house',3,'white','above','lake'),add('tree',2,'green','above','lake')]),
    ('Add two flowers of each color: pink and white and a tree, all near the bridge.',[add('flower',2,'pink','near','bridge'),add('flower',2,'white','near','bridge'),add('tree',relation='near',target='bridge')]),
    ('Build a house and not two trees, all near the lake.',[add('house',relation='near',target='lake')]),
    ('Build a house whose roof will have been painted blue.',[add('house',1,'blue')]),
    ('Build two cottages whose roofs shall already have been coloured purple.',[add('house',2,'purple')]),
    ('Plant a tree whose leaves will have recently been colored white.',[add('tree',1,'white')]),
    ('Add flowers whose petals will have been freshly painted pink.',[add('flower',1,'pink')]),
    ('Build four houses: one quarter whose roofs will have been painted red and the rest whose roofs will have been painted orange.',[add('house',1,'red'),add('house',3,'orange')]),
])
def test_supported_forms_and_spans(text,expected):
    result=parse(text)
    assert result['actions']==expected
    for span in result['tokens']+result['highlights']:
        assert text[span['start']:span['end']]==span['text']


@pytest.mark.parametrize('text',[
    'Plant six trees: one quarter blue and three quarters white.',
    'Plant trees: one quarter blue and three quarters white.',
    'Build eight houses: five quarters blue and the rest white.',
    'Build eight houses: -1 quarters red and the rest blue.',
    'Build eight houses: 1.5 quarters red and the rest blue.',
    'Add eight flowers: one quarter red and one quarter blue.',
    'Add three flowers of each color: red and black.',
    'Add three flowers of each color: red and white or blue.',
    'Add three flowers of each color: red and red.',
    'Add three blue flowers of each color: red and white.',
    'Add flowers of each color: red and white.',
    'Add -2 flowers of each color: red and white.',
    'Add a rock of each color: red and blue.',
    'Build a house and a tree, all not near the lake.',
    'Build a house near the lake and a tree, all behind the tower.',
    'Build a house and a tree, all near.',
    'Build a house and a tree, all near the lake behind the river.',
    'Remove houses and trees, all near the lake.',
    'Build a house whose roof will not have been painted red.',
    'Build a house whose roof will have never been painted green.',
    'Build a rock whose roof will have been painted blue.',
])
def test_invalid_ambiguous_or_unsafe_instructions_abstain(text):
    result=parse(text)
    assert result['actions']==[]
    assert result['warnings']


def test_shared_pronoun_landmarks_resolve_before_new_mixed_sources():
    text='Build two houses; add a tree and a flower, all between them; remove them.'
    result=parse(text)
    assert result['actions']==[add('house',2),add('tree',relation='between',targets=['house','house']),add('flower',relation='between',targets=['house','house']),remove('tree',1),remove('flower',1)]
    assert result['bindings']==[{'action_index':1,'target_from':[0]},{'action_index':2,'target_from':[0]},{'action_index':3,'remove_from':[1]},{'action_index':4,'remove_from':[2]}]


def test_rules_and_unicode_offsets_do_not_depend_on_spacy(monkeypatch):
    from backend import parser
    monkeypatch.setattr(parser,'NLP',None)
    text='Don’t add rocks; build eight houses: one quarter blue and three‑quarters white; remove them.'
    result=parser.parse(text)
    assert result['actions']==[add('house',2,'blue'),add('house',6,'white'),remove('house',8)]
    assert [h['text'] for h in result['highlights'] if h['role']=='quantity']==['eight','one quarter','three‑quarters']
    for span in result['highlights']+result['tokens']:
        assert text[span['start']:span['end']]==span['text']
