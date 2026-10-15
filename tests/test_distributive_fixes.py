"""Weather switches, each-color counts, inferred remainders and passive adverbs."""
import json
from pathlib import Path
import pytest
from backend.parser import parse
from tests.create_heldout_set import add, remove, setting

observed=[c for c in json.loads(Path(__file__).with_name('fresh_commands_v7.json').read_text(encoding='utf-8'))['cases'] if c['id'] in {'M41','M43','M45','M50'}]


@pytest.mark.parametrize('case',observed,ids=[c['id'] for c in observed])
def test_observed_errors(case):
    assert parse(case['text'])['actions']==case['expected_actions']


@pytest.mark.parametrize('text,expected',[
    ('Turn off the rain.',[setting('weather','clear')]),
    ('Turn the rain off.',[setting('weather','clear')]),
    ('Switch off snow.',[setting('weather','clear')]),
    ('Switch the snow off.',[setting('weather','clear')]),
    ('Turn on the rain.',[setting('weather','rain')]),
    ('Turn the snow on.',[setting('weather','snow')]),
    ('Turn off rain and turn on snow.',[setting('weather','clear'),setting('weather','snow')]),
    ('Make it rain and turn off the rain; plant a tree.',[setting('weather','rain'),setting('weather','clear'),add('tree')]),
    ('Don’t turn off the rain; add a flower.',[add('flower')]),
    ('Never switch the snow off.',[]),
    ('Do not turn on rain.',[]),
    ('Bring back daylight.',[setting('time','day')]),
    ('Place flowers: three each of pink and white.',[add('flower',3,'pink'),add('flower',3,'white')]),
    ('Build four cottages: two each of red and blue.',[add('house',2,'red'),add('house',2,'blue')]),
    ('Plant trees, two each of green, blue, and purple.',[add('tree',2,'green'),add('tree',2,'blue'),add('tree',2,'purple')]),
    ('Create three each of yellow and purple flowers.',[add('flower',3,'yellow'),add('flower',3,'purple')]),
    ('Build exactly two each of white and orange houses.',[add('house',2,'white'),add('house',2,'orange')]),
    ('Add flowers: twenty each of pink and blue.',[add('flower',16,'pink'),add('flower',16,'blue')]),
    ('Build twenty houses: four blue and the rest white.',[add('house',4,'blue'),add('house',16,'white')]),
    ('Add flowers: zero each of blue and pink.',[]),
    ('Plant trees: not two each of white and green.',[]),
    ('Add flowers: a pair each of pink and yellow beside the lake.',[add('flower',2,'pink','near','lake'),add('flower',2,'yellow','near','lake')]),
    ('Build houses: two each of blue and green; remove them.',[add('house',2,'blue'),add('house',2,'green'),remove('house',4)]),
    ('Build two houses: one each of pink and orange; put a tree between them.',[add('house',1,'pink'),add('house',1,'orange'),add('tree',relation='between',targets=['house','house'])]),
    ('Plant five trees: two yellow and the rest blue.',[add('tree',2,'yellow'),add('tree',3,'blue')]),
    ('Build six houses, one red and the remainder white.',[add('house',1,'red'),add('house',5,'white')]),
    ('Create five flowers: one purple, one pink, and the remaining ones yellow.',[add('flower',1,'purple'),add('flower',1,'pink'),add('flower',3,'yellow')]),
    ('Plant four green trees: one small one and the rest large ones.',[add('tree',1,'green'),add('tree',3,'green')]),
    ('Build four houses: one whose roof is blue and the rest with pink roofs.',[add('house',1,'blue'),add('house',3,'pink')]),
    ('Add three flowers: three red and the rest yellow.',[add('flower',3,'red')]),
    ('Build houses, a total of five: two blue and the rest orange; remove them.',[add('house',2,'blue'),add('house',3,'orange'),remove('house',5)]),
    ('Build two houses: one green and the rest purple; place a flower between them.',[add('house',1,'green'),add('house',1,'purple'),add('flower',relation='between',targets=['house','house'])]),
    ('Build a house whose roof has already been painted red.',[add('house',1,'red')]),
    ('Add two houses with roofs which have recently been coloured purple.',[add('house',2,'purple')]),
    ('Plant a tree whose leaves have been freshly colored blue.',[add('tree',1,'blue')]),
    ('Create flowers whose petals had just been painted orange.',[add('flower',1,'orange')]),
    ('Build a cottage with a roof that is newly painted pink near the river.',[add('house',1,'pink','near','river')]),
    ('Build three houses: one whose roof has previously been painted green and the rest whose roofs have just been painted yellow.',[add('house',1,'green'),add('house',2,'yellow')]),
])
def test_supported_forms(text,expected):
    result=parse(text)
    assert result['actions']==expected
    for span in result['highlights']+result['tokens']:
        assert text[span['start']:span['end']]==span['text']


@pytest.mark.parametrize('text',[
    'Create five flowers: three each of red and blue.',
    'Add flowers: -2 each of pink and white.',
    'Add flowers: 1.5 each of pink and white.',
    'Add flowers: three each of red or blue.',
    'Add flowers: three each of red and blue or yellow.',
    'Add flowers: three each of red and blue and brown.',
    'Add three each of red and black flowers.',
    'Add flowers: many each of red and blue.',
    'Add flowers: each of red and blue.',
    'Plant trees: two blue and the rest green.',
    'Plant three trees: four blue and the rest green.',
    'Plant four trees: the rest blue and two green.',
    'Plant four trees: one blue and the rest yellow and the remainder purple.',
    'Plant four trees: one blue and not the rest green.',
    'Build a cottage whose roof has never been painted blue.',
    'Build a cottage whose roof has not already been painted blue.',
    'Build a cottage whose roof has almost been painted blue.',
    'Add a rock whose roof has recently been painted blue.',
])
def test_ambiguous_or_unsupported_forms_abstain(text):
    result=parse(text)
    assert result['actions']==[]
    assert result['warnings']


def test_reference_bindings_remainder_highlights_and_no_spacy(monkeypatch):
    from backend import parser
    monkeypatch.setattr(parser,'NLP',None)
    text='Build four houses: one blue and the rest pink; remove them; turn off the rain.'
    result=parser.parse(text)
    assert result['actions']==[add('house',1,'blue'),add('house',3,'pink'),remove('house',4),setting('weather','clear')]
    assert result['bindings']==[{'action_index':2,'remove_from':[0,1]}]
    assert any(h['text']=='the rest' and h['role']=='quantity' for h in result['highlights'])
    for span in result['highlights']+result['tokens']:
        assert text[span['start']:span['end']]==span['text']


def test_distributive_quantity_highlight_is_not_duplicated():
    result=parse('Plant three each of green and purple trees.')
    assert [h['text'] for h in result['highlights'] if h['role']=='quantity']==['three']
