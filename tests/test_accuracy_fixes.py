"""Regression coverage promoted from the first diagnostic evaluation."""
import json
from pathlib import Path

import pytest
from backend.parser import parse

OLD = json.loads(Path(__file__).with_name("heldout_commands.json").read_text(encoding="utf-8"))["cases"]
TARGETS = {"negation", "settings", "quantifiers", "fronted_relations", "protected_mentions"}
CASES = [case for case in OLD if case["category"] in TARGETS]


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_prior_diagnostic_regressions(case):
    assert parse(case["text"])["actions"] == case["expected_actions"]


@pytest.mark.parametrize("text", [
    "Don’t erase any houses.", "Don‘t create bridges.", "Do not clear the world.",
    "Never plant trees, flowers, or rocks.", "Please don't remove the lake.",
    "Keep the trees, flowers, and houses.", "Leave the towers alone.",
    "Preserve the lake and protect the houses.", "Move the houses.",
    "I already have a lake.",
])
def test_non_creation_mentions_never_become_creations(text):
    assert parse(text)["actions"] == []


def test_painting_edits_existing_objects_without_creating_any():
    assert parse("Paint the house blue.")["actions"] == [{"action": "recolor", "type": "house", "count": 1, "color": "blue"}]


@pytest.mark.parametrize("text", [
    "Keep the houses, but build two trees.",
    "Leave the lake alone; plant two trees.",
    "Don’t build any houses, but plant two trees.",
])
def test_excluded_clause_does_not_suppress_next_positive_instruction(text):
    assert parse(text)["actions"] == [{"action": "add", "type": "tree", "count": 2, "color": None}]


@pytest.mark.parametrize("text", ["Make it not rain.", "Make it not snow.", "Make it night without rain."])
def test_negated_weather_clears_weather(text):
    assert {"action": "setting", "key": "weather", "value": "clear"} in parse(text)["actions"]


@pytest.mark.parametrize("text,count", [
    ("Plant eleven trees.", 11), ("Plant twelve trees.", 12),
    ("Plant sixteen trees.", 16), ("Plant a dozen trees.", 12),
    ("Plant half a dozen trees.", 6), ("Plant a pair of trees.", 2),
    ("Plant three pairs of trees.", 6), ("Plant two dozen trees.", 16),
    ("Plant twenty-one trees.", 16), ("Plant one hundred trees.", 16),
    ("Plant twenty‑one trees.", 16),
])
def test_cardinal_and_group_quantities(text, count):
    assert parse(text)["actions"][0]["count"] == count


@pytest.mark.parametrize("text", ["Add -3 trees.", "Add −3 trees.", "Add 2.5 trees.", "Add two or three trees.", "Add many trees."])
def test_invalid_or_ambiguous_quantities_abstain_with_a_notice(text):
    result = parse(text)
    assert result["actions"] == []
    assert result["warnings"]


@pytest.mark.parametrize("text,kind,relation,target", [
    ("Behind the castle, build a house.", "house", "above", "castle"),
    ("West of the tower plant a tree.", "tree", "left", "tower"),
    ("Beside the river, please place a rock.", "rock", "near", "river"),
    ("To the north of the river, build a rock.", "rock", "above", "river"),
])
def test_fronted_landmarks_are_not_created(text, kind, relation, target):
    assert parse(text)["actions"] == [{"action": "add", "type": kind, "count": 1, "color": None, "relation": relation, "target": target}]


def test_fronted_relation_applies_to_each_coordinated_subject():
    result = parse("Near the lake, build a house and plant two trees.")
    assert result["actions"][0]["target"] == "lake"
    # A new explicit verb starts a new instruction; placement is not inherited.
    assert "target" not in result["actions"][1]
    shared = parse("Near the lake, build a house and two trees.")["actions"]
    assert [a["target"] for a in shared] == ["lake", "lake"]


def test_fronted_removal_does_not_delete_unfiltered_type():
    result = parse("Near the lake, remove trees.")
    assert result["actions"] == []
    assert result["warnings"]


@pytest.mark.parametrize("text", [
    "Don’t add towers; near the lake, plant a dozen pink flowers.",
    "Keep the castle; between two houses, put a bridge.",
])
def test_original_unicode_and_fronted_span_offsets_are_preserved(text):
    result = parse(text)
    assert result["actions"]
    for span in result["highlights"] + result["tokens"]:
        assert text[span["start"]:span["end"]] == span["text"]


def test_bare_noun_phrase_remains_a_supported_description():
    assert parse("three red houses near the lake")["actions"][0] == {
        "action": "add", "type": "house", "count": 3, "color": "red", "relation": "near", "target": "lake"
    }
