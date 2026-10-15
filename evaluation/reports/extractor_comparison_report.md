# Rule-based grounding vs dependency-parse baseline

WordWorld drives the world with hand-written grounding rules (`backend/parser.py`). This report measures them against a grammar-driven alternative, `backend/dependency_baseline.py`, which reads the same actions from spaCy's dependency arcs (dobj, nummod, amod, prep/pobj, conj) using only the shared vocabulary, with no hand-written phrase patterns.

## Method and caveats

- **Commands:** 600 labelled commands: the 50-command development set, the held-out set and fresh sets v2–v10.
- **Scoring:** identical field definitions to `tests/evaluate_heldout.py`. Exact match compares every field of the ordered action list.
- **The rules have seen these sets.** After each set's first run, the rule parser was improved using its failures, so rule retest scores are optimistic. Their recorded **first-run** exact match on the 11 frozen sets was **442/550 (80%)**.
- **The baseline has not.** It was written against separate example sentences and frozen (SHA-256 `a3fa82150bd5…`) before its first run here; it is not tuned on these results.
- Fresh set v11 tests edits and cross-request references. Its context cases give the rules what the previous command touched; the baseline cannot use that context, which is part of what is being compared.
- Both are implementation-aware, hand-authored diagnostics, not independent accuracy estimates.

## Overall

| Metric | Rules (retest) | Dependency baseline |
|---|---|---|
| exact match | 557/600 (93%) | 138/600 (23%) |
| intent | 559/600 (93%) | 260/600 (43%) |
| entity count color | 560/600 (93%) | 194/600 (32%) |
| spatial | 147/153 (96%) | 41/153 (27%) |
| identical action lists | 27% of commands | |

## By set

| Set | Rules exact (retest) | Rules exact (first run) | Baseline exact | Baseline spatial |
|---|---|---|---|---|
| development | 50/50 (100%) | (development set) | 39/50 (78%) | 13/15 (87%) |
| heldout | 50/50 (100%) | 35/50 | 27/50 (54%) | 10/22 (45%) |
| fresh_v2 | 48/50 (96%) | 40/50 | 25/50 (50%) | 7/19 (37%) |
| fresh_v3 | 45/50 (90%) | 41/50 | 8/50 (16%) | 1/21 (5%) |
| fresh_v4 | 46/50 (92%) | 40/50 | 2/50 (4%) | 0/13 (0%) |
| fresh_v5 | 47/50 (94%) | 41/50 | 3/50 (6%) | 1/8 (12%) |
| fresh_v6 | 46/50 (92%) | 41/50 | 1/50 (2%) | 0/9 (0%) |
| fresh_v7 | 45/50 (90%) | 40/50 | 8/50 (16%) | 0/7 (0%) |
| fresh_v8 | 44/50 (88%) | 40/50 | 3/50 (6%) | 1/4 (25%) |
| fresh_v9 | 44/50 (88%) | 40/50 | 3/50 (6%) | 1/13 (8%) |
| fresh_v10 | 42/50 (84%) | 40/50 | 4/50 (8%) | 2/11 (18%) |
| fresh_v11 | 50/50 (100%) | 44/50 | 15/50 (30%) | 5/11 (45%) |

## Reading the results

The baseline is competitive on short, canonical commands (the development and held-out sets) but falls to single digits on the later fresh sets, which were written to probe counted partitions, totals, remainders, post-noun clauses and references. Dependency arcs locate the verb, its object and its prepositional phrases well; they do not say how a total splits into colored groups, which mention a pronoun means, or that a mention after 'keep' is protected rather than created. That missing layer is what the hand-written grounding rules supply, and it is why the world is driven by the rules while spaCy provides annotations.

Even against the rules' **first-run** scores, which the rules had never seen, the gap stays large.

## Where they differ

Examples where only the baseline is right show phrasings the rules still miss; examples where only the rules are right show what dependency arcs alone do not capture (partitions, totals, remainders, references, negated or protected mentions).

### Only the baseline is exactly right: 2

- **G46** “Make it day without any rain.”
  - expected `[{"action": "setting", "key": "time", "value": "day"}, {"action": "setting", "key": "weather", "value": "clear"}]`
  - rules `[{"action": "setting", "key": "time", "value": "day"}]`
  - baseline `[{"action": "setting", "key": "time", "value": "day"}, {"action": "setting", "key": "weather", "value": "clear"}]`
- **L50** “Make it daylight without any snow.”
  - expected `[{"action": "setting", "key": "time", "value": "day"}, {"action": "setting", "key": "weather", "value": "clear"}]`
  - rules `[{"action": "setting", "key": "time", "value": "day"}]`
  - baseline `[{"action": "setting", "key": "time", "value": "day"}, {"action": "setting", "key": "weather", "value": "clear"}]`

### Only the rules are exactly right (first 25): 421

- **D17** “Build a house and a castle”
  - expected `[{"action": "add", "type": "house", "count": 1, "color": null}, {"action": "add", "type": "castle", "count": 1, "color": null}]`
  - rules `[{"action": "add", "type": "house", "count": 1, "color": null}, {"action": "add", "type": "castle", "count": 1, "color": null}]`
  - baseline `[{"action": "add", "type": "house", "count": 1, "color": null}]`
- **D21** “Get rid of the rocks”
  - expected `[{"action": "remove", "type": "rock", "count": "all"}]`
  - rules `[{"action": "remove", "type": "rock", "count": "all"}]`
  - baseline `[]`
- **D22** “Clear away two flowers”
  - expected `[{"action": "remove", "type": "flower", "count": 2}]`
  - rules `[{"action": "remove", "type": "flower", "count": 2}]`
  - baseline `[]`
- **D28** “Make it rain then make it snow”
  - expected `[{"action": "setting", "key": "weather", "value": "rain"}, {"action": "setting", "key": "weather", "value": "snow"}]`
  - rules `[{"action": "setting", "key": "weather", "value": "rain"}, {"action": "setting", "key": "weather", "value": "snow"}]`
  - baseline `[{"action": "setting", "key": "weather", "value": "rain"}]`
- **D33** “Build a bridge across the river and three trees”
  - expected `[{"action": "add", "type": "bridge", "count": 1, "color": null, "relation": "across", "target": "river"}, {"action": "add", "type": "tree", "count": 3, "color": null}]`
  - rules `[{"action": "add", "type": "bridge", "count": 1, "color": null, "relation": "across", "target": "river"}, {"action": "add", "type": "tree", "count": 3, "color": null}]`
  - baseline `[{"action": "add", "type": "bridge", "count": 1, "color": null, "relation": "across", "target": "river"}]`
- **D37** “Add zero trees”
  - expected `[]`
  - rules `[]`
  - baseline `[{"action": "add", "type": "tree", "count": 0, "color": null}]`
- **D38** “Plant three forests”
  - expected `[{"action": "add", "type": "tree", "count": 3, "color": null}]`
  - rules `[{"action": "add", "type": "tree", "count": 3, "color": null}]`
  - baseline `[]`
- **D39** “Plant a couple of trees”
  - expected `[{"action": "add", "type": "tree", "count": 2, "color": null}]`
  - rules `[{"action": "add", "type": "tree", "count": 2, "color": null}]`
  - baseline `[]`
- **D45** “Put a bridge between the house”
  - expected `[]`
  - rules `[]`
  - baseline `[{"action": "add", "type": "bridge", "count": 1, "color": null}]`
- **D49** “Put a lake behind the houses, a bridge across the river, and three trees beside the road”
  - expected `[{"action": "add", "type": "lake", "count": 1, "color": null, "relation": "above", "target": "house"}, {"action": "add", "type": "bridge", "count": 1, "color": null, "relation": "across", "target": "river"}, {"action": "add", "type": "tree", "count": 3, "color": null, "relation": "near", "target": "road"}]`
  - rules `[{"action": "add", "type": "lake", "count": 1, "color": null, "relation": "above", "target": "house"}, {"action": "add", "type": "bridge", "count": 1, "color": null, "relation": "across", "target": "river"}, {"action": "add", "type": "tree", "count": 3, "color": null, "relation": "near", "target": "road"}]`
  - baseline `[{"action": "add", "type": "lake", "count": 1, "color": null, "relation": "above", "target": "house"}]`
- **D50** “Add a red house and a tree”
  - expected `[{"action": "add", "type": "house", "count": 1, "color": "red"}, {"action": "add", "type": "tree", "count": 1, "color": null}]`
  - rules `[{"action": "add", "type": "house", "count": 1, "color": "red"}, {"action": "add", "type": "tree", "count": 1, "color": null}]`
  - baseline `[{"action": "add", "type": "house", "count": 1, "color": "red"}]`
- **H02** “Plant seven green trees south of the tower.”
  - expected `[{"action": "add", "type": "tree", "count": 7, "color": "green", "relation": "below", "target": "tower"}]`
  - rules `[{"action": "add", "type": "tree", "count": 7, "color": "green", "relation": "below", "target": "tower"}]`
  - baseline `[{"action": "add", "type": "tree", "count": 7, "color": "green"}]`
- **H03** “Place 6 yellow blossoms north of the fortress.”
  - expected `[{"action": "add", "type": "flower", "count": 6, "color": "yellow", "relation": "above", "target": "castle"}]`
  - rules `[{"action": "add", "type": "flower", "count": 6, "color": "yellow", "relation": "above", "target": "castle"}]`
  - baseline `[]`
- **H04** “Give me three white cabins west of the pond.”
  - expected `[{"action": "add", "type": "house", "count": 3, "color": "white", "relation": "left", "target": "lake"}]`
  - rules `[{"action": "add", "type": "house", "count": 3, "color": "white", "relation": "left", "target": "lake"}]`
  - baseline `[]`
- **H06** “Put a boulder in the center of the garden.”
  - expected `[{"action": "add", "type": "rock", "count": 1, "color": null, "relation": "inside", "target": "flower"}]`
  - rules `[{"action": "add", "type": "rock", "count": 1, "color": null, "relation": "inside", "target": "flower"}]`
  - baseline `[{"action": "add", "type": "rock", "count": 1, "color": null}]`
- **H07** “Show a lighthouse at the back of the cottages.”
  - expected `[{"action": "add", "type": "tower", "count": 1, "color": null, "relation": "above", "target": "house"}]`
  - rules `[{"action": "add", "type": "tower", "count": 1, "color": null, "relation": "above", "target": "house"}]`
  - baseline `[]`
- **H09** “Insert a mountain to the right of the bridge.”
  - expected `[{"action": "add", "type": "mountain", "count": 1, "color": null, "relation": "right", "target": "bridge"}]`
  - rules `[{"action": "add", "type": "mountain", "count": 1, "color": null, "relation": "right", "target": "bridge"}]`
  - baseline `[]`
- **H10** “Grow a woodland close to the road.”
  - expected `[{"action": "add", "type": "tree", "count": 6, "color": null, "relation": "near", "target": "road"}]`
  - rules `[{"action": "add", "type": "tree", "count": 6, "color": null, "relation": "near", "target": "road"}]`
  - baseline `[{"action": "add", "type": "tree", "count": 1, "color": null}]`
- **H14** “Plant three flowers within the castle.”
  - expected `[{"action": "add", "type": "flower", "count": 3, "color": null, "relation": "inside", "target": "castle"}]`
  - rules `[{"action": "add", "type": "flower", "count": 3, "color": null, "relation": "inside", "target": "castle"}]`
  - baseline `[{"action": "add", "type": "flower", "count": 3, "color": null}]`
- **H15** “Build a hut, a tower, and a road.”
  - expected `[{"action": "add", "type": "house", "count": 1, "color": null}, {"action": "add", "type": "tower", "count": 1, "color": null}, {"action": "add", "type": "road", "count": 1, "color": null}]`
  - rules `[{"action": "add", "type": "house", "count": 1, "color": null}, {"action": "add", "type": "tower", "count": 1, "color": null}, {"action": "add", "type": "road", "count": 1, "color": null}]`
  - baseline `[{"action": "add", "type": "house", "count": 1, "color": null}]`
- **H16** “Delete 4 boulders, then plant six blossoms.”
  - expected `[{"action": "remove", "type": "rock", "count": 4}, {"action": "add", "type": "flower", "count": 6, "color": null}]`
  - rules `[{"action": "remove", "type": "rock", "count": 4}, {"action": "add", "type": "flower", "count": 6, "color": null}]`
  - baseline `[{"action": "add", "type": "flower", "count": 6, "color": null}]`
- **H17** “Cut down a couple of trees; create a pond.”
  - expected `[{"action": "remove", "type": "tree", "count": 2}, {"action": "add", "type": "lake", "count": 1, "color": null}]`
  - rules `[{"action": "remove", "type": "tree", "count": 2}, {"action": "add", "type": "lake", "count": 1, "color": null}]`
  - baseline `[{"action": "add", "type": "lake", "count": 1, "color": null}]`
- **H18** “Erase one bridge and place three yellow cottages.”
  - expected `[{"action": "remove", "type": "bridge", "count": 1}, {"action": "add", "type": "house", "count": 3, "color": "yellow"}]`
  - rules `[{"action": "remove", "type": "bridge", "count": 1}, {"action": "add", "type": "house", "count": 3, "color": "yellow"}]`
  - baseline `[{"action": "add", "type": "house", "count": 3, "color": "yellow"}]`
- **H19** “Clear the map; show a river and a bridge.”
  - expected `[{"action": "reset"}, {"action": "add", "type": "river", "count": 1, "color": null}, {"action": "add", "type": "bridge", "count": 1, "color": null}]`
  - rules `[{"action": "reset"}, {"action": "add", "type": "river", "count": 1, "color": null}, {"action": "add", "type": "bridge", "count": 1, "color": null}]`
  - baseline `[]`
- **H22** “Stop the snow and make it sunshine.”
  - expected `[{"action": "setting", "key": "weather", "value": "clear"}, {"action": "setting", "key": "time", "value": "day"}]`
  - rules `[{"action": "setting", "key": "weather", "value": "clear"}, {"action": "setting", "key": "time", "value": "day"}]`
  - baseline `[{"action": "setting", "key": "weather", "value": "clear"}]`

Full per-command predictions: `evaluation/results/extractor_comparison.json`. Regenerate with `python -m tests.compare_extractors`; CI runs it with `--check`.
