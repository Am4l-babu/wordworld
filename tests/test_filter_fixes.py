"""Round twelve: place filters for edits and removals, more fractions, 'each' and semicolon wordings."""
import json
from pathlib import Path
import pytest
from backend.parser import parse

DATASET = json.loads(Path(__file__).with_name("fresh_commands_v12.json").read_text(encoding="utf-8"))
# S39 asks for 18 white flowers; commands are capped at 16 objects per action, so the correct output is a capped
# group plus a notice. The frozen label stays as written and the report counts it as a miss.
LABEL_EXCEEDS_CAP = {"S39"}
# Probes that remain outside the grammar. Listed so they stay visible; if one starts passing, pytest reports XPASS.
KNOWN_GAPS = {
    "S44": "'in each of A and B, two per color' (count given after the list)",
    "S46": "'flowers in pink and white, four of each' (trailing each-count)",
    "S48": "'two clusters of three flowers' (group multiplication)",
}
CASES = [c for c in DATASET["cases"] if c["id"] not in LABEL_EXCEEDS_CAP]
PARAMS = [pytest.param(c, id=c["id"], marks=pytest.mark.xfail(reason=KNOWN_GAPS[c["id"]], strict=True) if c["id"] in KNOWN_GAPS else ()) for c in CASES]


@pytest.mark.parametrize("case", PARAMS)
def test_round_twelve_set_after_fixes(case):
    assert parse(case["text"], case.get("context"))["actions"] == case["expected_actions"]


def test_the_over_cap_label_is_capped_with_a_notice_not_silently_truncated():
    result = parse("Create twenty flowers: one tenth pink and nine tenths white.")
    assert [(a["count"], a["color"]) for a in result["actions"]] == [(2, "pink"), (16, "white")]
    assert "Limited flower quantity to 16." in result["warnings"]


@pytest.mark.parametrize("text,groups", [
    ("Build twelve houses: a sixth red and the rest blue.", [(2, "red"), (10, "blue")]),
    ("Build eight houses: three eighths red and the rest blue.", [(3, "red"), (5, "blue")]),
    ("Plant ten trees: three pink; the rest green.", [(3, "pink"), (7, "green")]),
    ("Plant ten trees: three pink; four white; the rest green.", [(3, "pink"), (4, "white"), (3, "green")]),
    ("Place a pair of flowers in each of red and yellow.", [(2, "red"), (2, "yellow")]),
    ("Plant three trees in each of pink, white and green.", [(3, "pink"), (3, "white"), (3, "green")]),
])
def test_new_partition_wordings(text, groups):
    assert [(a["count"], a["color"]) for a in parse(text)["actions"]] == groups


def test_a_semicolon_before_a_new_instruction_still_separates_instructions():
    result = parse("Create one flower of each color: red and white; remove them.")
    assert [a["action"] for a in result["actions"]] == ["add", "add", "remove"]


@pytest.mark.parametrize("text,subset", [("Build three houses, then make two of them red.", 2), ("Build two houses, then paint both of them blue.", 2)])
def test_counted_pronouns_edit_part_of_a_group(text, subset):
    edit = parse(text)["actions"][1]
    assert edit["action"] == "recolor" and edit["count"] == subset


@pytest.mark.parametrize("text", ["Build three houses, then paint both of them blue.", "Build two houses and a tree, then paint two of them blue.",
                                  "Build two houses, then paint five of them blue."])
def test_counted_pronouns_that_do_not_fit_are_explained_not_guessed(text):
    result = parse(text)
    assert not any(a["action"] == "recolor" for a in result["actions"]) and result["warnings"]


@pytest.mark.parametrize("text", ["Add a tower next to a red rock.", "Add a tree next to a white flower."])
def test_a_color_that_no_object_uses_is_reported_never_silently_dropped(text):
    result = parse(text)
    assert len(result["actions"]) == 1 and result["actions"][0]["color"] is None
    assert result["warnings"] and "was not used" in result["warnings"][0]


def test_used_colors_and_explained_skips_raise_no_extra_notice():
    assert parse("Build two red houses near the lake.")["warnings"] == []
    assert not any("was not used" in w for w in parse("Don't build six cottages: two red and four blue; plant a flower.")["warnings"])
