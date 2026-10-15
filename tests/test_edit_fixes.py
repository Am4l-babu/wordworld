"""Round eleven: edits, references and fractions, including the fixes made after its first run."""
import json
from pathlib import Path
import pytest
from backend.parser import parse

DATASET = json.loads(Path(__file__).with_name("fresh_commands_v11.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("case", DATASET["cases"], ids=[c["id"] for c in DATASET["cases"]])
def test_round_eleven_set_after_fixes(case):
    assert parse(case["text"], case.get("context"))["actions"] == case["expected_actions"]


@pytest.mark.parametrize("text,actions", [
    ("Make both trees pink.", [{"action": "recolor", "type": "tree", "count": 2, "color": "pink"}]),
    ("Paint the three red flowers white.", [{"action": "recolor", "type": "flower", "count": 3, "color": "white", "filter_color": "red"}]),
    ("Make the towers shorter.", [{"action": "resize", "type": "tower", "count": "all", "scale": 0.8}]),
    ("Give the tree purple leaves.", [{"action": "recolor", "type": "tree", "count": 1, "color": "purple"}]),
    ("Move the tree a little closer to the house.", [{"action": "move", "type": "tree", "count": 1, "relation": "near", "target": "house"}]),
    ("Shift the bridge right a bit.", [{"action": "move", "type": "bridge", "count": 1, "direction": "right", "distance": "small"}]),
])
def test_post_first_run_fixes_generalise(text, actions):
    assert parse(text)["actions"] == actions


@pytest.mark.parametrize("text", ["Give me two houses.", "Make two trees pink.", "Give a castle to the village."])
def test_creation_wording_with_give_or_counts_still_creates_or_abstains(text):
    assert not any(a["action"] in {"recolor", "resize", "move"} for a in parse(text)["actions"])
