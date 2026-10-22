# Ablation: what each component contributes

Each row removes **one** component from the full rule parser and re-scores all 650 labelled commands by exact match against the gold actions. Intervals are 95% Wilson score intervals. The rules were developed against these sets after each set's first run, so their scores are optimistic; the first-run scores below are the honest ones. The baseline was frozen before it ever ran here.

| Configuration | Exact match | 95% interval | Δ vs full |
|---|---|---|---|
| Full rules | 608/650 (93.5%) | 91.4% – 95.2% | — |
| − cross-request context | 601/650 (92.5%) | 90.2% – 94.2% | -7 |
| − place filters | 579/650 (89.1%) | 86.5% – 91.2% | -29 |
| − edit grammar | 549/650 (84.5%) | 81.5% – 87.0% | -59 |
| − spaCy (tokenizer only) | 608/650 (93.5%) | 91.4% – 95.2% | +0 |
| Dependency baseline | 146/650 (22.5%) | 19.4% – 25.8% | -462 |

**Reading the table.** Removing spaCy changes nothing: the rules never used it for actions, only for token annotations (a claim the project makes and this row verifies). Removing the edit grammar costs exactly the commands that edit existing objects, and removing context costs exactly the commands that refer to an earlier command. The baseline falls far below every ablation of the rules, so the hand-written grounding, not the parse tree, carries the system.

## By set

| Set | Full rules | First run (frozen) | Baseline |
|---|---|---|---|
| development | 50/50 | (development set) | 39/50 |
| heldout | 50/50 | 35/50 | 27/50 |
| fresh_v2 | 48/50 | 40/50 | 25/50 |
| fresh_v3 | 45/50 | 41/50 | 8/50 |
| fresh_v4 | 46/50 | 40/50 | 2/50 |
| fresh_v5 | 47/50 | 41/50 | 3/50 |
| fresh_v6 | 46/50 | 41/50 | 1/50 |
| fresh_v7 | 46/50 | 40/50 | 8/50 |
| fresh_v8 | 45/50 | 40/50 | 3/50 |
| fresh_v9 | 45/50 | 40/50 | 3/50 |
| fresh_v10 | 44/50 | 40/50 | 4/50 |
| fresh_v11 | 50/50 | 44/50 | 15/50 |
| fresh_v12 | 46/50 | 41/50 | 8/50 |

## By linguistic family (approximate: families are assigned from category names)

| Family | Commands | Full rules | Baseline | Gap |
|---|---|---|---|---|
| counted partitions and fractions | 147 | 87.8% | 8.8% | +79% |
| references and pronouns | 86 | 93.0% | 5.8% | +87% |
| edits and place filters | 74 | 100.0% | 29.7% | +70% |
| spatial relations | 68 | 98.5% | 20.6% | +78% |
| colors and attributes | 68 | 98.5% | 0.0% | +99% |
| development set (uncategorised) | 50 | 100.0% | 78.0% | +22% |
| negation, protection, removal | 42 | 97.6% | 57.1% | +40% |
| weather and time | 30 | 93.3% | 36.7% | +57% |
| quantities | 30 | 100.0% | 36.7% | +63% |
| coordination and multi-action sentences | 28 | 100.0% | 14.3% | +86% |
| clause structure | 16 | 43.8% | 0.0% | +44% |
| paraphrase and lexical variation | 11 | 63.6% | 27.3% | +36% |

## Typo handling

On 524 commands carrying one synthetic typo (seed 4, never inspected), exact match is **7.3%** for the rules alone (5.3% – 9.8%) and **99.8%** when the first “Did you mean” suggestion is applied (98.9% – 100.0%). The app never applies a suggestion itself; this measures the ceiling if the person accepts it. The 9% is conditional on a typo landing in a vocabulary word the grammar needs, chosen on purpose to stress the system; it is not a prediction of how often people mistype.

## Limits

These are hand-authored, implementation-aware sets: the author wrote both grammar and gold, and the rules saw each set after its first run. Differences of a few commands between configurations are within the intervals. Family assignment is heuristic. Nothing here estimates accuracy on strangers' sentences; the user-test kit (`docs/USER_TESTING.md`) exists to measure that.
