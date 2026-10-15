import json
from pathlib import Path

import pytest
from backend import parser

CASES = json.loads(Path(__file__).with_name("commands.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("case", CASES, ids=[case["text"] for case in CASES])
def test_labeled_actions(case):
    assert parser.parse(case["text"])["actions"] == case["actions"]


@pytest.mark.parametrize("text", [
    "  BUILD two RED houses near the lake. Then plant a tree!",
    "✨ Put a bridge between the house and the lake",
    "Remove two rocks, then add three blue flowers",
])
def test_explanation_spans_are_exact_original_substrings(text):
    result = parser.parse(text)
    for span in result["highlights"] + result["tokens"]:
        assert text[span["start"]:span["end"]] == span["text"]
    for token in result["tokens"]:
        if token["head"] is not None:
            assert text[token["head_start"]:].startswith(token["head"])
    assert result["grounding"] == "rules"


def test_rules_work_without_spacy(monkeypatch):
    monkeypatch.setattr(parser, "NLP", None)
    monkeypatch.setattr(parser, "NLP_STATUS", "rules")
    result = parser.parse("Put a bridge between two houses")
    assert result["actions"][0]["targets"] == ["house", "house"]
    assert all(token["head"] is None and token["dep"] == "" for token in result["tokens"])


@pytest.mark.parametrize("text", ["Don't delete houses", "Add 0 trees", "Add it", "Put a bridge between the house", "Remove trees near the lake"])
def test_unsupported_or_negated_commands_explain_why(text):
    result = parser.parse(text)
    assert result["actions"] == []
    assert result["warnings"]


@pytest.mark.parametrize("text", ["", "  ", "x" * 1401])
def test_invalid_input(text):
    with pytest.raises(ValueError):
        parser.parse(text)


@pytest.mark.parametrize("text", ["Don't remove houses, trees", "No trees and flowers", "Do not add houses, flowers, rocks"])
def test_negation_covers_a_noun_list(text):
    assert parser.parse(text)["actions"] == []


def test_chained_landmarks_are_not_created():
    result = parser.parse("Add a tree near the lake behind the castle")
    assert [action["type"] for action in result["actions"]] == ["tree"]
    assert result["actions"][0]["target"] == "lake"
    assert result["warnings"]


@pytest.mark.parametrize("text", ["Put a bridge between three houses", "Put a bridge between a house and two lakes"])
def test_between_rejects_more_than_two_landmarks(text):
    result = parser.parse(text)
    assert result["actions"] == []
    assert result["warnings"]


@pytest.mark.parametrize("text,count", [
    ("Remove the bridge", 1),
    ("Get rid of the house.", 1),
    ("Remove every house", "all"),
    ("Remove the houses", "all"),
    ("Remove the village", "all"),
    ("Remove two houses", 2),
])
def test_singular_definite_removal_removes_one_object(text, count):
    assert [a["count"] for a in parser.parse(text)["actions"]] == [count]
