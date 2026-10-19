# Testing WordWorld with real people

The measured accuracy so far comes from sentences the author wrote. This guide collects sentences from people who have never seen the
grammar, to find what it misses. A 10-minute session per person is enough.

## What the app records, and what it does not

While someone plays, their browser keeps a **private test log**: each sentence typed, what the language engine did with it, any "Did you mean…?" it
showed and whether they used it, and replies they marked **Not what I meant** (with an optional note on what they expected). Nothing is
sent to a server. It stays in that browser until the person opens **Share & save → Test log → Download my test log** and sends you the file.
The log never contains the island, only the sentences, and it can be cleared from the same dialog.

## Before a session

1. Deploy the version you want to test. Open the live site once yourself and check **Share & save → Test log** is there.
2. Tell each person what you will keep (their sentences) and that they can clear the log or skip sending it. Ask them **not to type personal
   information**. Because the files contain exactly what people typed, treat them as research data: don't publish or commit them
   (`evaluation/usertests/*.json` is git-ignored).
3. Give each person a fresh browser profile or a private window, so the log starts empty. Do **not** show them the example sentences, the help
   dialog or the README: the point is to see what people try on their own.

## The session (about 10 minutes)

Say only this: *"This program turns sentences into a small island. Try to make the island look the way you want by typing. If a reply is not
what you meant, press **Not what I meant** and tell me what you wanted."*

Then three short tasks, in this order, without hints:

1. **Build.** "Make a village you would like to live in."
2. **Change.** "Now change three things about it that you don't like."
3. **Your own idea.** "Make something you have been imagining. Anything."

Stay quiet while they work. Write down, on paper, anything they say out loud and anything they try that is not typing (clicking, dragging,
looking for a button). Stop after ten minutes or when they run out of ideas. Ask: *What did you try that you expected to work?*

At the end, have them open **Share & save → Test log → Download my test log** and send you the file.

## Analysing the files

Put the downloaded files in `evaluation/usertests/` and run:

```powershell
.\.venv\Scripts\python.exe -m tests.analyze_usertests --report evaluation\usertests\summary.md --csv evaluation\usertests\candidates.csv
```

The report shows how many commands worked, how many were understood as nothing, which **words the grammar does not know** in the commands that
failed (these are the vocabulary gaps), how often "Did you mean…?" helped, what testers said they expected, and, first of all, the commands
they flagged **even though the world changed**: those are wrong results with no warning, the worst failures.

`candidates.csv` lists every failed, flagged or drifted command with the parser's current answer. The `expected_actions` column is empty on
purpose: fill it in by hand, because the analyzer must not grade the parser's own output.

## Turning findings into the next round

1. Pick the commands worth keeping and write their expected actions yourself.
2. Freeze them as a new set (copy `tests/create_fresh_set_v12.py` to `..._v13.py`) **before** changing the grammar, and run the parser on it
   once, untuned. That first-run score is the honest number for real users.
3. Then fix the failures, and report the first run and the retest separately, as every earlier round does.

## How much to trust the result

Ten people typing sentences will not give you a percentage you can quote with confidence. Use the results to find **kinds** of failure (a missing
word, a phrasing, a feature people expect) and to see whether the common ones are fixed in the next round; report counts, not accuracy claims. Say
how many people took part, how they were chosen, and that the author wrote the grammar.
