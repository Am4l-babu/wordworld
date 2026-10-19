"""'Did you mean ...?' when a misspelled word costs a command its meaning, or part of it."""
import pytest
from backend import parser
from backend.suggest import GRAMMAR_WORDS, VOCABULARY_SET, candidates, close_match, distance, suggest
from tests.test_api import request


@pytest.mark.parametrize("a,b,expected", [("nigth", "night", 1), ("bleu", "blue", 1), ("tres", "tree", 1), ("lak", "lake", 1), ("house", "house", 0), ("abc", "xyz", 3)])
def test_an_adjacent_swap_counts_as_one_edit(a, b, expected):
    assert distance(a, b) == expected


@pytest.mark.parametrize("typo,fixed", [
    ("flwer", "flower"), ("casle", "castle"), ("betwen", "between"), ("bleu", "blue"), ("lak", "lake"), ("nigth", "night"),
    # a typo ending in "s" most likely meant a plural
    ("tres", "trees"), ("houes", "houses"),
])
def test_close_vocabulary_words_are_found(typo, fixed):
    assert close_match(typo) == fixed


@pytest.mark.parametrize("word", ["the", "and", "two", "hello", "with", "island", "xyz", "it", "big", "there", "whose", "remaining", "three", "larger"])
def test_real_words_and_unrelated_words_are_left_alone(word):
    assert candidates(word) == []


def test_the_vocabulary_is_read_from_the_grammar_so_its_own_words_are_never_typos():
    # "show" is an add-verb in the grammar; it is one letter from "snow" but must never be "corrected".
    assert {"show", "whose", "remaining", "generate", "insert"} <= GRAMMAR_WORDS <= VOCABULARY_SET
    assert close_match("show") is None
    result = suggest("Leave all mountains alone, then show a lightohuse.", parser.parse)
    assert not result or "snow" not in result[0]["text"]


@pytest.mark.parametrize("text,fixed", [
    ("Paint the tres blue", "Paint the trees blue"),
    ("Build two reed houses near the lak", "Build two red houses near the lake"),  # two typos, neither fix alone is enough
    ("Put a bridge betwen two houses", "Put a bridge between two houses"),
    ("PLANT A TRE", "PLANT A TREE"),
    ("Add a flwer", "Add a flower"),
    ("Create a dozrn red homes beside the path.", "Create a dozen red homes beside the path."),
])
def test_a_typo_gets_a_corrected_sentence_that_really_parses_better(text, fixed):
    [suggestion] = suggest(text, parser.parse)
    assert suggestion["text"] == fixed
    assert parser.parse(fixed)["actions"]
    for change in suggestion["changes"]:
        assert text[change["start"]:change["end"]] == change["from"]


def test_a_typo_that_only_costs_part_of_the_command_is_flagged_as_replacing_what_was_applied():
    # The house is still built, but "bule" is silently ignored: a partial, wrong world.
    original = parser.parse("Build two red houses and one bule house.")
    assert original["actions"] and original["actions"][-1]["color"] is None
    [suggestion] = suggest("Build two red houses and one bule house.", parser.parse)
    assert suggestion["text"] == "Build two red houses and one blue house." and suggestion["replaces"] is True
    [fresh] = suggest("Add a flwer", parser.parse)
    assert fresh["replaces"] is False


@pytest.mark.parametrize("text", ["Hello there friend", "How about we make some stuff", "Add the", "Add a cat", "Make it night with rain"])
def test_no_suggestion_when_nothing_would_improve(text):
    assert suggest(text, parser.parse) == []


def test_correct_commands_never_get_a_suggestion():
    for text in ["Build two red houses near the lake.", "Paint the trees near the lake red", "Plant ten trees: three pink; the rest green.",
                 "Add a tower next to a red rock.", "Put a bridge between two houses", "Make it night with rain", "Show a lighthouse behind the castle"]:
        assert suggest(text, parser.parse) == [], text


def test_suggestions_respect_context_and_only_count_when_they_parse():
    # Only the fixable word changes; an unrelated unknown word stays as the person typed it.
    assert suggest("Add a flwer and a unicrn", parser.parse)[0]["text"] == "Add a flower and a unicrn"
    assert suggest("make it blu", parser.parse, [{"type": "house", "count": 1}])[0]["text"] == "make it blue"
    assert suggest("make it blu", parser.parse) == []  # without a referent the corrected sentence still parses to nothing


def test_the_api_returns_suggestions_for_typos_and_none_for_good_commands():
    typo = request("POST", "/api/parse", json={"text": "Paint the tres blue"}).json()
    assert typo["actions"] == [] and typo["suggestions"][0]["text"] == "Paint the trees blue"
    partial = request("POST", "/api/parse", json={"text": "Build one bule house"}).json()
    assert partial["actions"] and partial["suggestions"][0]["text"] == "Build one blue house" and partial["suggestions"][0]["replaces"]
    fine = request("POST", "/api/parse", json={"text": "Add a tree"}).json()
    assert fine["actions"] and fine["suggestions"] == []
    nothing = request("POST", "/api/parse", json={"text": "Hello there friend"}).json()
    assert nothing["actions"] == [] and nothing["suggestions"] == []
