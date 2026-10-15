"""Observed reference/coordination errors promoted into regressions."""
import json
from pathlib import Path

import pytest
from backend.parser import parse

HERE = Path(__file__).parent
old = json.loads((HERE/'heldout_commands.json').read_text(encoding='utf-8'))['cases']
second = json.loads((HERE/'fresh_commands_v2.json').read_text(encoding='utf-8'))['cases']
CASES = [c for c in old + second if c['category'] in {'coreference', 'coordination_ellipsis', 'relation_paraphrase'}]


@pytest.mark.parametrize('case', CASES, ids=[c['id'] for c in CASES])
def test_observed_failures(case):
    assert parse(case['text'])['actions'] == case['expected_actions']


@pytest.mark.parametrize('text', [
    'Place a bridge spanning the stream.',
    'Put a bridge crossing the creek.',
])
def test_crossing_landmark_is_not_a_creation(text):
    assert parse(text)['actions'] == [{'action': 'add', 'type': 'bridge', 'count': 1, 'color': None, 'relation': 'across', 'target': 'river'}]


def test_unknown_relation_does_not_turn_its_landmark_into_an_add_subject():
    result = parse('Put a bridge straddling the river and add a flower.')
    assert not any(a.get('type') == 'river' for a in result['actions'])
    assert result['warnings']
    assert result['actions'][-1]['type'] == 'flower'


def test_pronouns_never_leak_between_requests():
    parse('Build a house.')
    result = parse('Remove it.')
    assert result['actions'] == []
    assert result['warnings']


@pytest.mark.parametrize('text', ['Plant five trees; remove it.', 'Build a house and a tree; remove one of them.'])
def test_ambiguous_references_abstain(text):
    result = parse(text)
    assert all(a['action'] != 'remove' for a in result['actions'])
    assert result['warnings']


def test_removal_is_bounded_to_introduced_objects_and_tracks_remaining_count():
    actions = parse('Plant five trees; remove two of them; remove them.')['actions']
    assert actions[-2:] == [{'action':'remove','type':'tree','count':2}, {'action':'remove','type':'tree','count':3}]
    bounded = parse('Plant three trees; remove ten of them.')
    assert bounded['actions'][-1] == {'action':'remove','type':'tree','count':3}
    assert bounded['warnings']


def test_plural_removal_can_refer_to_a_mixed_collection():
    actions = parse('Build a house and a tower; remove them.')['actions']
    assert actions[-2:] == [{'action':'remove','type':'house','count':1}, {'action':'remove','type':'tower','count':1}]


def test_reset_invalidates_references_and_settings_do_not_create_from_it():
    result = parse('Build a house; clear the world; remove it.')
    assert result['actions'] == [{'action':'add','type':'house','count':1,'color':None}, {'action':'reset'}]
    assert len(parse('Build a house; make it night; make it rain.')['actions']) == 3


def test_coordinated_colors_share_a_relation_and_are_valid_antecedents():
    actions = parse('Build one red and one blue house near the lake; put a tree between them.')['actions']
    assert [a['color'] for a in actions[:2]] == ['red','blue']
    assert all(a['target'] == 'lake' for a in actions[:2])
    assert actions[-1]['targets'] == ['house','house']


def test_coordinated_negation_only_excludes_its_own_group():
    assert parse('Build one red and not one blue house.')['actions'] == [{'action':'add','type':'house','count':1,'color':'red'}]


def test_comma_coordination_and_compound_number_and_are_distinguished():
    actions = parse('Build two red, three blue, and one yellow house.')['actions']
    assert [(a['count'],a['color']) for a in actions] == [(2,'red'),(3,'blue'),(1,'yellow')]
    assert parse('Build one hundred and two red houses.')['actions'][0]['count'] == 16


def test_reference_and_coordination_annotations_keep_original_offsets():
    text = 'Don’t add a rock; build one red and one blue house; put a tree between them.'
    result = parse(text)
    assert any(h['role'] == 'reference' for h in result['highlights'])
    for span in result['tokens'] + result['highlights']:
        assert text[span['start']:span['end']] == span['text']


def test_reference_rules_work_without_spacy(monkeypatch):
    from backend import parser
    monkeypatch.setattr(parser, 'NLP', None)
    assert parser.parse('Create a tower; put a tree behind it.')['actions'][-1]['target'] == 'tower'


def test_comma_separated_nouns_form_one_reference_collection():
    actions = parse('Build a house, a tower, and a tree; remove them.')['actions']
    assert actions[-3:] == [{'action':'remove','type':'house','count':1}, {'action':'remove','type':'tower','count':1}, {'action':'remove','type':'tree','count':1}]


def test_qualified_reference_removal_does_not_delete_a_landmark():
    result = parse('Build a house; remove it beside the lake.')
    assert result['actions'] == [{'action':'add','type':'house','count':1,'color':None}]
    assert result['warnings']


def test_unsupported_pronoun_statement_never_creates_its_predicate_noun():
    result = parse('Plant a tree; it is a house.')
    assert result['actions'] == [{'action':'add','type':'tree','count':1,'color':None}]
    assert result['warnings']


def test_unsupported_noun_connection_abstains_from_the_whole_clause():
    result = parse('Put a bridge straddling a river tree.')
    assert result['actions'] == []
    assert result['warnings']
