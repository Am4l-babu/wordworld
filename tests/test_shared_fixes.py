"""Storm stopping, even half partitions, comma placement and future passives."""
import json
from pathlib import Path
import pytest
from backend.parser import parse
from tests.create_heldout_set import add,remove,setting

observed=[c for c in json.loads(Path(__file__).with_name('fresh_commands_v8.json').read_text(encoding='utf-8'))['cases'] if c['id'] in {'N42','N43','N45','N49'}]


@pytest.mark.parametrize('case',observed,ids=[c['id'] for c in observed])
def test_observed_errors(case):
    assert parse(case['text'])['actions']==case['expected_actions']


@pytest.mark.parametrize('text,expected',[
    ('Stop the storm.',[setting('weather','clear')]),
    ('End the shower.',[setting('weather','clear')]),
    ('Make it rain and stop the storm.',[setting('weather','rain'),setting('weather','clear')]),
    ('Stop the storm and turn on snow.',[setting('weather','clear'),setting('weather','snow')]),
    ('Don’t stop the storm; add a tree.',[add('tree')]),
    ('Do not end the shower.',[]),
    ('Never stop raining.',[]),
    ('Make it dawn.',[setting('time','day')]),
    ('Build six houses: half blue and half white.',[add('house',3,'blue'),add('house',3,'white')]),
    ('Place ten flowers, half pink and half yellow.',[add('flower',5,'pink'),add('flower',5,'yellow')]),
    ('Add trees, a total of eight: half purple and half green.',[add('tree',4,'purple'),add('tree',4,'green')]),
    ('Build four houses: half with red roofs and half whose roofs are yellow.',[add('house',2,'red'),add('house',2,'yellow')]),
    ('Plant six trees: half of them blue and half of them orange.',[add('tree',3,'blue'),add('tree',3,'orange')]),
    ('Plant four green trees: half small ones and half large ones.',[add('tree',2,'green'),add('tree',2,'green')]),
    ('Add four flowers: half red and the rest pink.',[add('flower',2,'red'),add('flower',2,'pink')]),
    ('Build two houses: half white and half purple; put a flower between them.',[add('house',1,'white'),add('house',1,'purple'),add('flower',relation='between',targets=['house','house'])]),
    ('Add flowers, a total of zero: half purple and half orange.',[]),
    ('Build forty houses: half green and half blue.',[add('house',16,'green'),add('house',16,'blue')]),
    ('Plant trees: two blue and three green, all near the lake.',[add('tree',2,'blue','near','lake'),add('tree',3,'green','near','lake')]),
    ('Build four houses: half blue and half yellow, all behind the castle.',[add('house',2,'blue','above','castle'),add('house',2,'yellow','above','castle')]),
    ('Create flowers: two each of pink and white, all beside the road.',[add('flower',2,'pink','near','road'),add('flower',2,'white','near','road')]),
    ('Build three houses: one orange and the rest purple, all left of the lake; remove them.',[add('house',1,'orange','left','lake'),add('house',2,'purple','left','lake'),remove('house',3)]),
    ('Build houses, one green and one white, all between the river and the tower.',[add('house',1,'green','between',targets=['river','tower']),add('house',1,'white','between',targets=['river','tower'])]),
    ('Build a house whose roof will be painted blue.',[add('house',1,'blue')]),
    ('Build two homes with roofs that shall be coloured purple.',[add('house',2,'purple')]),
    ('Add a tree whose leaves will be freshly colored orange.',[add('tree',1,'orange')]),
    ('Place flowers whose petals will be painted pink near the pond.',[add('flower',1,'pink','near','lake')]),
    ('Build four homes: half whose roofs will be painted white and half whose roofs will be painted yellow.',[add('house',2,'white'),add('house',2,'yellow')]),
])
def test_supported_forms_and_exact_spans(text,expected):
    result=parse(text)
    assert result['actions']==expected
    for span in result['tokens']+result['highlights']:
        assert text[span['start']:span['end']]==span['text']


@pytest.mark.parametrize('text',[
    'Build five houses: half red and half blue.',
    'Add flowers: half pink and half white.',
    'Build four houses: half red and half blue and half white.',
    'Build four houses: half red.',
    'Build four houses: half red and not half blue.',
    'Build four houses and half blue and half green.',
    'Build four houses: half blue and half red, all not near the lake.',
    'Build a house whose roof will not be painted blue.',
    'Build a house whose roof will never be painted yellow.',
    'Build a rock whose roof will be painted blue.',
    'Build a house whose roof will be painted blue and red.',
])
def test_ambiguous_unmapped_or_negated_forms_abstain(text):
    result=parse(text)
    assert result['actions']==[]
    assert result['warnings']


def test_no_spacy_and_partition_reference_binding(monkeypatch):
    from backend import parser
    monkeypatch.setattr(parser,'NLP',None)
    text='Build four houses: half blue and half white, all near the lake; remove them; stop the storm.'
    result=parser.parse(text)
    assert result['actions']==[add('house',2,'blue','near','lake'),add('house',2,'white','near','lake'),remove('house',4),setting('weather','clear')]
    assert result['bindings']==[{'action_index':2,'remove_from':[0,1]}]
    assert [h['text'] for h in result['highlights'] if h['role']=='quantity']==['four','half','half']
