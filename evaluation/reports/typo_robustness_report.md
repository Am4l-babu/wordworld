# Typo robustness and the “Did you mean…?” suggester

The grounding rules need exact vocabulary, so one misspelled word turns a command into nothing or, worse, into a partial result that quietly ignores the word (`one bule house` still builds the house, in no color). The suggester (`backend/suggest.py`) tries the nearest vocabulary words for each unfamiliar word (edit distance, adjacent swaps count as one edit) and keeps a correction only if re-parsing the sentence is **measurably better**: fewer notices, or more of the sentence understood. The final sentence must produce actions. It never applies a correction itself: the app shows it and the person decides. The vocabulary is read from the grammar's own regex patterns, so a word the parser understands (`show`, `whose`, `remaining`) can never be mistaken for a typo.

## Method

Every labelled command (650 across the development, held-out and eleven fresh sets) that the rules already get exactly right is corrupted with **one** synthetic typo in a vocabulary word of at least four letters: a deletion, a duplicated letter, an adjacent swap, or a substitution with a QWERTY neighbour. The first letter is kept, as in most real typing errors. Commands with no gold actions are skipped.

- **harmless**: the corrupted command still parses to the gold actions
- **recovered**: it did not, but the first suggestion parses to the gold actions
- **wrong fix**: a suggestion was offered but parses to something else
- **missed**: nothing was offered
- **silent error**: the corrupted command parses to *different* actions and no suggestion is made, so the person gets a wrong world without a hint

**Seeds.** The suggester was developed against seed 1. Seed 2 was viewed while drafting the first version of this report; that exposed a real tie-break bias (a longer plural won because it highlights more text), fixed on principle. Seed 3 was then used as the untouched seed, and its two failures were both **typos in negation words** (`nefer remove them` removed what the person had forbidden), because the score treated the correct “Skipped a negated instruction” notice as a sign of confusion. Deliberate-skip notices no longer count against a correction, and restoring a negation word counts as progress whenever it changes what will be done. Seeds 2 and 3 are therefore reported as *reviewed*. The headline numbers use **seed 4**, whose results nobody inspected before this report was generated.

| Seed | Corrupted | Harmless | Recovered | Wrong fix | Missed | Recovery of the rest | Wrong-fix rate | Silent errors |
|---|---|---|---|---|---|---|---|---|
| 1 (tuning) | 529 | 40 | 485 | 1 | 3 | 99% | 0.2% | 3 |
| 2 (reviewed) | 528 | 36 | 490 | 1 | 1 | 100% | 0.2% | 1 |
| 3 (reviewed) | 530 | 50 | 480 | 0 | 0 | 100% | 0.0% | 0 |
| **4 (untouched)** | 524 | 38 | 485 | 0 | 1 | 100% | 0.0% | 1 |

## False alarms

- **Already-correct commands:** the suggester was run on all 541 labelled commands the rules parse exactly right: **0 suggestions**.
- **Typos the rules already tolerated** (seed 4): 0 suggestions that would change the actions; 12 that keep exactly the same actions and only tidy the spelling (and drop a notice).

## By typo kind (seed 4)

| Kind | Harmless | Recovered | Wrong fix | Missed |
|---|---|---|---|---|
| deletion | 12 | 114 | 0 | 1 |
| duplication | 8 | 125 | 0 | 0 |
| substitution | 8 | 133 | 0 | 0 |
| swap | 10 | 113 | 0 | 0 |

## What still goes wrong (seed 4)

### Wrong fixes

- none

### Missed

- “Build one hunded and three blue cottages.” (deletion: hunded for hundred)

### Silent errors (the typo changed the meaning, and nothing was suggested)

- “Build one hunded and three blue cottages.” (deletion: hunded for hundred)

## Limits

Synthetic noise is not human typing: real errors include phonetic spellings, missing spaces and autocorrect substitutions that this does not model. A word that is valid English but not in the vocabulary (`horse` for `house`) can be offered as a correction; that is why a suggestion is only ever shown, never applied. Two equally close words cannot be told apart without more context (`towes` is one edit from both `towers` and `towns`). A real English word that is also a one-letter-off typo (`there` for `three`) is left alone on purpose. Recovery is measured against the gold actions, not against what a person meant.
