"""Guard the suggester's measured quality; the full three-seed report is tests/evaluate_typos.py."""
from tests.evaluate_typos import REPORT_SEED, clean_false_alarms, run, summarise


def test_the_suggester_recovers_typos_without_changing_meaning_or_crying_wolf():
    summary = summarise(run(REPORT_SEED))
    assert summary["corrupted"] > 400
    assert summary["recovery_rate"] >= 0.97, summary
    assert summary["wrong_fix_rate"] <= 0.02, summary
    assert summary["harmless_false_alarms"] == 0, "a suggestion must never change the meaning of a command that already parsed correctly"
    assert summary["silent_errors"] <= 0.02 * summary["corrupted"], summary


def test_commands_the_rules_already_get_right_never_trigger_a_suggestion():
    clean = clean_false_alarms()
    assert clean["checked"] > 500
    assert clean["false_alarms"] == 0, clean["examples"]
