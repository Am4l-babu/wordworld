"""Editing existing objects by language, and references that carry across requests."""
import pytest
from backend import parser
from tests.test_api import request


def actions(text, context=None):
    return parser.parse(text, context)["actions"]


@pytest.mark.parametrize("text,expected", [
    ("Paint the house blue", [{"action": "recolor", "type": "house", "count": 1, "color": "blue"}]),
    ("Make the trees purple", [{"action": "recolor", "type": "tree", "count": "all", "color": "purple"}]),
    ("Change the color of the flowers to white", [{"action": "recolor", "type": "flower", "count": "all", "color": "white"}]),
    ("Change the house to blue", [{"action": "recolor", "type": "house", "count": 1, "color": "blue"}]),
    ("Paint the red house blue", [{"action": "recolor", "type": "house", "count": 1, "color": "blue", "filter_color": "red"}]),
    ("Make two of the houses yellow", [{"action": "recolor", "type": "house", "count": 2, "color": "yellow"}]),
    ("Make the houses bigger", [{"action": "resize", "type": "house", "count": "all", "scale": 1.25}]),
    ("Make the castle much smaller", [{"action": "resize", "type": "castle", "count": 1, "scale": 0.67}]),
    ("Shrink the tower a bit", [{"action": "resize", "type": "tower", "count": 1, "scale": 0.89}]),
    ("Enlarge every rock", [{"action": "resize", "type": "rock", "count": "all", "scale": 1.25}]),
    ("Move the tree to the left of the lake", [{"action": "move", "type": "tree", "count": 1, "relation": "left", "target": "lake"}]),
    ("Move the castle between the lake and the tower", [{"action": "move", "type": "castle", "count": 1, "relation": "between", "target": "lake", "targets": ["lake", "tower"]}]),
    ("Move the castle a bit to the left", [{"action": "move", "type": "castle", "count": 1, "direction": "left", "distance": "small"}]),
    ("Shift the houses far up", [{"action": "move", "type": "house", "count": "all", "direction": "up", "distance": "large"}]),
    ("Make the trees purple and the houses red", [{"action": "recolor", "type": "tree", "count": "all", "color": "purple"},
                                                  {"action": "recolor", "type": "house", "count": "all", "color": "red"}]),
    ("Paint the house blue, the tree pink", [{"action": "recolor", "type": "house", "count": 1, "color": "blue"},
                                              {"action": "recolor", "type": "tree", "count": 1, "color": "pink"}]),
])
def test_edits_of_existing_objects(text, expected):
    assert actions(text) == expected


@pytest.mark.parametrize("text", [
    "Make two blue houses", "Make two houses blue", "Make it night", "Turn the rain off", "Make a castle", "Make it rain",
])
def test_creation_and_weather_wording_is_not_read_as_an_edit(text):
    assert not any(a["action"] in {"recolor", "resize", "move"} for a in actions(text))


def test_edits_report_what_they_cannot_show():
    result = parser.parse("Paint the castle blue")
    assert result["actions"] == [] and "Castles have no color" in result["warnings"][0]
    result = parser.parse("Paint the house")
    assert result["actions"] == [] and "Could not tell how to paint" in result["warnings"][0]
    result = parser.parse("Don't paint the house blue")
    assert result["actions"] == [] and result["warnings"]
    result = parser.parse("Move the tree behind")
    assert result["actions"] == [] and "named landmark" in result["warnings"][0]
    assert parser.parse("Paint the house blue banana")["warnings"] == ["Ignored words after the edit: 'banana'."]


def test_edited_objects_become_referents_within_a_request():
    result = parser.parse("Build two houses and make them bigger")
    assert result["actions"][1] == {"action": "resize", "type": "house", "count": 2, "scale": 1.25}
    assert result["bindings"] == [{"action_index": 1, "edit_from": [0]}]
    result = parser.parse("Paint the house blue and move it left")
    assert result["actions"][1]["action"] == "move" and result["bindings"] == [{"action_index": 1, "edit_from": [0]}]


def test_context_carries_references_across_requests():
    result = parser.parse("make it blue", [{"type": "house", "count": 1}])
    assert result["actions"] == [{"action": "recolor", "type": "house", "count": 1, "color": "blue"}]
    assert result["bindings"] == [{"action_index": 0, "edit_from": [-1]}]
    assert result["resolutions"][0]["earlier"] is True
    result = parser.parse("Remove them", [{"type": "house", "count": 2}, {"type": "tree", "count": 1}])
    assert [a["type"] for a in result["actions"]] == ["house", "tree"]
    assert [b["remove_from"] for b in result["bindings"]] == [[-1], [-2]]
    result = parser.parse("Put a flower next to it", [{"type": "castle", "count": 1}])
    assert result["actions"][0]["target"] == "castle" and result["bindings"] == [{"action_index": 0, "target_from": [-1]}]
    # 'it' still prefers a referent introduced earlier in the same request.
    assert parser.parse("Build a tree and paint it pink", [{"type": "house", "count": 1}])["actions"][1]["type"] == "tree"
    # Agreement is still enforced, and without context nothing is guessed.
    assert parser.parse("paint it red", [{"type": "tree", "count": 2}])["actions"] == []
    assert parser.parse("make it blue")["actions"] == []


def test_api_validates_context():
    ok = request("POST", "/api/parse", json={"text": "make it blue", "context": [{"type": "house", "count": 1}]})
    assert ok.status_code == 200 and ok.json()["actions"][0]["action"] == "recolor"
    for context in [[{"type": "dragon", "count": 1}], [{"type": "house", "count": 0}], [{"type": "house", "count": 1}] * 13]:
        assert request("POST", "/api/parse", json={"text": "make it blue", "context": context}).status_code == 422
