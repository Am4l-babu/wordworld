"""The ablation tooling must be exact, and must never leave a component switched off."""
import pytest
from backend import edits, parser
from tests.ablation import configuration, family, wilson


def test_wilson_interval_matches_known_values():
    low, high = wilson(50, 100)
    assert (round(low, 3), round(high, 3)) == (0.404, 0.596)
    assert wilson(0, 10)[0] == 0.0 and wilson(10, 10)[1] == 1.0
    assert wilson(0, 0) is None
    low, high = wilson(608, 650)
    assert low < 608 / 650 < high


@pytest.mark.parametrize("name", ["no_edits", "no_filters", "no_spacy"])
def test_a_removed_component_changes_behaviour_inside_and_is_restored_after(name):
    before = (parser.read_edit, parser.FILTER_RELATIONS, edits.read_location_filter, parser.NLP)
    probe = "Paint the trees near the lake red"
    full = parser.parse(probe)["actions"]
    with configuration(name):
        ablated = parser.parse(probe)["actions"]
    assert (parser.read_edit, parser.FILTER_RELATIONS, edits.read_location_filter, parser.NLP) == before
    assert parser.parse(probe)["actions"] == full
    if name == "no_spacy":
        assert ablated == full  # spaCy only annotates
    else:
        assert ablated != full


def test_restoration_happens_even_when_the_body_raises():
    before = parser.read_edit
    with pytest.raises(RuntimeError):
        with configuration("no_edits"):
            raise RuntimeError("boom")
    assert parser.read_edit is before


@pytest.mark.parametrize("category,expected", [("quarter_partition", "counted partitions and fractions"), ("filter_remove", "edits and place filters"),
                                               ("context_recolor", "references and pronouns"), ("subordinate_creation", "clause structure"), ("nonsense_xyz", "other")])
def test_families_group_fine_grained_categories(category, expected):
    assert family(category) == expected
