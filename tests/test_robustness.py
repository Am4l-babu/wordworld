"""Inputs that used to be misread, rejected silently, or slow."""
import time
import pytest
from backend import parser
from tests.test_api import request


@pytest.mark.parametrize("text,expected", [
    ("Add 1,000 rocks", [("add", "rock", 16)]),
    ("Plant 12,345 trees", [("add", "tree", 16)]),
    ("Remove 1,000 trees", [("remove", "tree", 16)]),
    ("Add 1,000 trees and 2,500 flowers", [("add", "tree", 16), ("add", "flower", 16)]),
    ("Plant 20 trees, 5 houses and 1,200 rocks", [("add", "tree", 16), ("add", "house", 5), ("add", "rock", 16)]),
    ("Paint 1,000 trees green", [("recolor", "tree", 120)]),
    # A comma that is not followed by exactly three digits still separates numbers or lists.
    ("Add 3,5 trees", [("add", "tree", 3), ("add", "tree", 5)]),
    ("Add 3 trees, 5 flowers", [("add", "tree", 3), ("add", "flower", 5)]),
])
def test_thousands_separators_are_one_number(text, expected):
    result = parser.parse(text)
    assert [(a["action"], a["type"], a["count"]) for a in result["actions"]] == expected
    assert all("Limited" in w for w in result["warnings"])


@pytest.mark.parametrize("text", ["Paint the 0 trees green", "Paint the zero trees green", "Move the 0 houses left", "Paint 0 of the trees green"])
def test_edits_of_zero_objects_are_skipped_with_a_notice(text):
    result = parser.parse(text)
    assert result["actions"] == [] and any("zero-count" in w for w in result["warnings"])


def test_very_long_lists_are_refused_clearly_not_parsed_slowly():
    with pytest.raises(ValueError, match="too many list parts"):
        parser.parse("houses: " + "one blue; " * 60)
    response = request("POST", "/api/parse", json={"text": "Build houses: " + "one blue, " * 60})
    assert response.status_code == 400 and "too many list parts" in response.json()["detail"]
    # The limit sits well above realistic commands: forty parts still parse.
    assert parser.parse("Build houses: " + "one blue, " * 35)["actions"]


@pytest.mark.parametrize("text", [
    "Build houses: " + "one blue, " * 39,
    "houses: " + "one blue; " * 39,
    "Build " + "two red houses, " * 39,
    "Paint the trees " + "near the lake " * 80 + "red",
    "and " * 340,
    "the " * 340 + "house",
    "Remove " + "the trees and " * 90,
])
def test_adversarial_inputs_parse_within_a_second(text):
    started = time.perf_counter()
    try:
        parser.parse(text[:1400])
    except ValueError:
        pass
    assert time.perf_counter() - started < 1.0
