"""The analyzer that turns downloaded test logs into findings."""
import csv
import json
from tests.analyze_usertests import analyse, load, markdown, unknown_words, write_csv


def entry(i, text, outcome="applied", actions=None, **extra):
    return {"id": i, "at": "2026-10-19T10:00:00Z", "text": text, "outcome": outcome, "device": "desktop", "context": [],
            "actions": actions if actions is not None else [], "warnings": [], "message": "", "model": "spacy",
            "suggestion": None, "replaces": False, "suggestionAccepted": False, "flagged": False, "note": "", **extra}


def log(path, entries, **overrides):
    path.write_text(json.dumps({"schema": 1, "app": "wordworld-testlog", "exportedAt": "2026-10-19T10:00:00Z", "entries": entries, **overrides}), encoding="utf-8")


TREE = [{"action": "add", "type": "tree", "count": 1, "color": None}]


def make_folder(tmp_path):
    log(tmp_path / "ana.json", [
        entry("a1", "Add a tree", actions=TREE),
        entry("a2", "Build a unicorn stable", "nothing", warnings=["No supported object"]),
        entry("a3", "Build two red houses", actions=[{"action": "add", "type": "house", "count": 1, "color": None}], flagged=True, note="I said two"),
        entry("a4", "Paint the tres blue", "nothing", suggestion="Paint the trees blue", suggestionAccepted=True),
    ])
    log(tmp_path / "ben.json", [
        entry("a1", "Add a tree", actions=TREE),  # same id as ana's: de-duplicated
        entry("b1", "Make a sparkly unicorn meadow", "nothing", device="phone"),
        entry("b2", "Plant a tree", actions=[{"action": "add", "type": "rock", "count": 1}]),  # logged result differs from today's parser
    ])
    (tmp_path / "broken.json").write_text("{not json", encoding="utf-8")
    log(tmp_path / "other.json", [entry("z", "x")], app="something-else")
    return tmp_path


def test_files_load_deduplicated_and_bad_files_are_reported_not_fatal(tmp_path):
    entries, problems = load(make_folder(tmp_path))
    assert [e["id"] for e in entries] == ["a1", "a2", "a3", "a4", "b1", "b2"]
    assert {p.split(":")[0] for p in problems} == {"broken.json", "other.json"}


def test_rates_gaps_suggestions_and_drift(tmp_path):
    entries, _ = load(make_folder(tmp_path))
    stats = analyse(entries)
    assert (stats["testers"], stats["commands"], stats["phone"]) == (2, 6, 1)
    assert stats["outcomes"] == {"applied": 3, "nothing": 3}
    assert stats["flagged"] == 1 and stats["flagged_but_applied"] == 1
    assert (stats["suggestions_shown"], stats["suggestions_accepted"]) == (1, 1)
    # "Plant a tree" was logged as a rock; "Build two red houses" now builds two houses: both differ from today's parser
    assert stats["drift"] == 2
    gaps = dict(stats["gaps"])
    assert gaps["unicorn"] == 2 and "tree" not in gaps and "the" not in gaps


def test_unfamiliar_words_ignore_vocabulary_and_function_words():
    assert unknown_words("Build a sparkly unicorn with the red house") == ["sparkly", "unicorn"]


def test_the_report_names_the_dangerous_cases_and_what_testers_expected(tmp_path):
    entries, problems = load(make_folder(tmp_path))
    text = markdown(analyse(entries), entries, problems)
    assert "Flagged although the world changed" in text and "“Build two red houses” → *I said two*" in text
    assert "| unicorn | 2 |" in text and "Skipped files" in text


def test_candidates_for_labelling_leave_the_gold_column_empty(tmp_path):
    entries, _ = load(make_folder(tmp_path))
    analyse(entries)
    out = tmp_path / "candidates.csv"
    write_csv(out, entries)
    rows = list(csv.DictReader(out.open(encoding="utf-8")))
    assert {r["id"] for r in rows} == {"a2", "a3", "a4", "b1", "b2"}  # the plain success is not a candidate
    assert all(r["expected_actions"] == "" for r in rows)
    assert json.loads(next(r for r in rows if r["id"] == "a3")["current_actions"])[0]["count"] == 2


def test_an_empty_folder_is_a_clear_message_not_a_crash(tmp_path):
    entries, problems = load(tmp_path)
    assert "No commands to analyse" in markdown(analyse(entries), entries, problems)
