"""Colon partitions, total-of word order and explicit remainder arithmetic."""
import json
from pathlib import Path
import pytest
from backend.parser import parse
from tests.create_heldout_set import add, remove

cases=json.loads(Path(__file__).with_name('fresh_commands_v6.json').read_text(encoding='utf-8'))['cases']
observed=[c for c in cases if c['id'] in {'L41','L42','L43'}]


@pytest.mark.parametrize('case',observed,ids=[c['id'] for c in observed])
def test_observed_failures(case):
    assert parse(case['text'])['actions']==case['expected_actions']


@pytest.mark.parametrize('text,expected',[
    ('Add trees: two green and one purple.',[add('tree',2,'green'),add('tree',1,'purple')]),
    ('Build three houses: one with a blue roof, two with red roofs.',[add('house',1,'blue'),add('house',2,'red')]),
    ('Build two houses: one blue one and one yellow one.',[add('house',1,'blue'),add('house',1,'yellow')]),
    ('Build three houses with green roofs: one small one and two large ones.',[add('house',1,'green'),add('house',2,'green')]),
    ('Add houses, a total of four.',[add('house',4)]),
    ('Plant trees, the total of half a dozen.',[add('tree',6)]),
    ('Add flowers: a total of exactly seven.',[add('flower',7)]),
    ('Add rocks, a total of twenty-one.',[add('rock',16)]),
    ('Add towers, a total of two pairs near the lake.',[add('tower',4,relation='near',target='lake')]),
    ('Build houses, a total of five: two blue and three green.',[add('house',2,'blue'),add('house',3,'green')]),
    ('Add flowers, a total of zero.',[]),
    ('Add flowers, a total of -3.',[]),
    ('Add flowers, a total of 1.5.',[]),
    ('Add flowers, not a total of five.',[]),
    ('Plant five trees: two green and the remaining three purple.',[add('tree',2,'green'),add('tree',3,'purple')]),
    ('Place six flowers, two pink and remaining four white.',[add('flower',2,'pink'),add('flower',4,'white')]),
    ('Build houses, a total of four: one red and the remaining three blue.',[add('house',1,'red'),add('house',3,'blue')]),
    ('Plant two trees: two green and the remaining zero yellow.',[add('tree',2,'green')]),
    ('Behind the lake, build three cottages: one red and the remaining two blue.',[add('house',1,'red','above','lake'),add('house',2,'blue','above','lake')]),
    ('Add a house and flowers, a total of three.',[add('house'),add('flower',3)]),
    ('Build houses, a total of three with purple roofs; remove them.',[add('house',3,'purple'),remove('house',3)]),
    ('Build two houses: one green and one blue; put a flower between them.',[add('house',1,'green'),add('house',1,'blue'),add('flower',relation='between',targets=['house','house'])]),
])
def test_scoped_colons_totals_and_remainders(text,expected):
    assert parse(text)['actions']==expected


@pytest.mark.parametrize('text',[
    'Build three houses: one blue and one red.',
    'Build two houses: three large ones.',
    'Build three houses with green roofs: one red and two blue.',
    'Add houses, a total of five or six.',
    'Add trees, a total of many.',
    'Add trees, a total of three, five total.',
    'Plant five trees, two green and the remaining four yellow.',
    'Plant trees, two green and the remaining three yellow.',
    'Plant five trees and the remaining three blue.',
    'Plant five trees: the remaining three green and two blue.',
    'Plant five trees: two green and remaining one blue and remaining two yellow.',
])
def test_conflicting_or_undefined_counts_abstain(text):
    result=parse(text)
    assert result['actions']==[]
    assert result['warnings']


def test_spans_and_bindings_keep_original_colons_and_unicode():
    text='Don’t add rocks; build three houses: one green and the remaining two blue; remove them.'
    result=parse(text)
    assert result['actions']==[add('house',1,'green'),add('house',2,'blue'),remove('house',3)]
    assert result['bindings']==[{'action_index':2,'remove_from':[0,1]}]
    assert any(h['text']=='remaining' and h['role']=='quantity' for h in result['highlights'])
    for span in result['highlights']+result['tokens']:
        assert text[span['start']:span['end']]==span['text']


def test_rules_do_not_depend_on_spacy(monkeypatch):
    from backend import parser
    monkeypatch.setattr(parser,'NLP',None)
    assert parser.parse('Add trees, a total of four: one purple and remaining three green.')['actions']==[add('tree',1,'purple'),add('tree',3,'green')]
