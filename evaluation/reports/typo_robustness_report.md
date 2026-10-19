# Typo robustness and the “Did you mean…?” suggester

The grounding rules need exact vocabulary, so one misspelled word turns a command into nothing or, worse, into a partial result that quietly ignores the word (`one bule house` still builds the house, in no color). The suggester (`backend/suggest.py`) tries the nearest vocabulary words for each unfamiliar word (edit distance, adjacent swaps count as one edit) and keeps a correction only if re-parsing the sentence is **measurably better**: fewer notices, or more of the sentence understood. The final sentence must produce actions. It never applies a correction itself: the app shows it and the person decides. The vocabulary is read from the grammar's own regex patterns, so a word the parser understands (`show`, `whose`, `remaining`) can never be mistaken for a typo.

## Method

Every labelled command (650 across the development, held-out and twelve fresh sets) that the rules already get exactly right is corrupted with **one** synthetic typo in a vocabulary word of at least four letters: a deletion, a duplicated letter, an adjacent swap, or a substitution with a QWERTY neighbour. The first letter is kept, as in most real typing errors. Commands with no gold actions are skipped.

- **harmless**: the corrupted command still parses to the gold actions
- **recovered**: it did not, but the first suggestion parses to the gold actions
- **wrong fix**: a suggestion was offered but parses to something else
- **missed**: nothing was offered
- **silent error**: the corrupted command parses to *different* actions and no suggestion is made, so the person gets a wrong world without a hint

**Seeds.** The suggester was developed against seed 1. Seed 2 was viewed once while writing the first draft of this report; that exposed a real tie-break bias (a longer plural won because it highlights more text), which was fixed on principle, so seed 2 no longer counts as untouched. The headline numbers use **seed 3**, whose results nobody inspected before this report was generated.

| Seed | Corrupted | Harmless | Recovered | Wrong fix | Missed | Recovery of the rest | Wrong-fix rate | Silent errors |
|---|---|---|---|---|---|---|---|---|
| 1 (tuning) | 529 | 40 | 485 | 1 | 3 | 99% | 0.2% | 3 |
| 2 (reviewed) | 528 | 36 | 488 | 1 | 3 | 99% | 0.2% | 2 |
| **3 (untouched)** | 530 | 50 | 478 | 0 | 2 | 100% | 0.0% | 2 |

## False alarms

- **Already-correct commands:** the suggester was run on all 541 labelled commands the rules parse exactly right: **0 suggestions**.
- **Typos the rules already tolerated** (seed 3): 0 suggestions that would change the actions; 8 that keep exactly the same actions and only tidy the spelling (and drop a notice).

## By typo kind (seed 3)

| Kind | Harmless | Recovered | Wrong fix | Missed |
|---|---|---|---|---|
| deletion | 13 | 119 | 0 | 1 |
| duplication | 16 | 120 | 0 | 0 |
| substitution | 13 | 125 | 0 | 1 |
| swap | 8 | 114 | 0 | 0 |

## What still goes wrong (seed 3)

### Wrong fixes

- none

### Missed

- “Add two rocks; nefer remove them.” (substitution: nefer for never)
- “Place trees: not two whte and four green.” (deletion: whte for white)

### Silent errors (the typo changed the meaning, and nothing was suggested)

- “Add two rocks; nefer remove them.” (substitution: nefer for never)
- “Place trees: not two whte and four green.” (deletion: whte for white)

## Limits

Synthetic noise is not human typing: real errors include phonetic spellings, missing spaces and autocorrect substitutions that this does not model. A word that is valid English but not in the vocabulary (`horse` for `house`) can be offered as a correction; that is why a suggestion is only ever shown, never applied. Two equally close words cannot be told apart without more context (`towes` is one edit from both `towers` and `towns`). A real English word that is also a one-letter-off typo (`there` for `three`) is left alone on purpose. Recovery is measured against the gold actions, not against what a person meant.
