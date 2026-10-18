# Round twelve: place filters, filtered removal and wording gaps

This round adds a place filter for edits and removals (`paint the trees near the lake red`, `remove the flowers next to the house`), matched against the scene geometry with the same cone placement uses; `sixths`..`ninths`; `in each of red and yellow`; semicolons inside a colon-partition; counted pronouns (`make two of them red`); and a notice whenever a typed color is not applied.

## Frozen first run

`tests/fresh_commands_v12.json` (SHA-256 `156ae7af7ca1…`) was labelled by `tests/create_fresh_set_v12.py` and frozen before the parser ever ran on it; the backend fingerprint matched at evaluation time. The filter grammar already existed, so these commands test it on unseen sentences, not on the sentences used to build it.

| Metric | First run |
|---|---|
| exact match | 41/50 |
| intent | 43/50 |
| entity count color | 42/50 |
| spatial | 7/7 |
| settings | 1/1 |
| core cases | 39/40 |
| broader probes | 2/10 |

**1 core miss, and it is a labelling error:** **S39** “Create twenty flowers: one tenth pink and nine tenths white.” expects `[{"action": "add", "type": "flower", "count": 2, "color": "pink"}, {"action": "add", "type": "flower", "count": 18, "color": "white"}]` but the documented 16-object cap per action gives `[{"action": "add", "type": "flower", "count": 2, "color": "pink"}, {"action": "add", "type": "flower", "count": 16, "color": "white"}]` with the notice “Limited flower quantity to 16.”. The parser behaved as documented; the gold was wrong. Frozen labels are never edited, so it stays a miss in every number here, and `tests/test_filter_fixes.py` asserts the capped output instead.

All 8 other misses were broader probes:

- **S41** “Paint the trees red near the lake.” — expected `[{"action": "recolor", "type": "tree", "count": "all", "color": "red", "filter_relation": "near", "filter_target": "lake"}]`, got `[{"action": "recolor", "type": "tree", "count": "all", "color": "red"}]` (Ignored words after the edit: 'near the lake'.)
- **S44** “Plant trees in each of pink and white, two per color.” — expected `[{"action": "add", "type": "tree", "count": 2, "color": "pink"}, {"action": "add", "type": "tree", "count": 2, "color": "white"}]`, got `[{"action": "add", "type": "tree", "count": 1, "color": null}]` (No supported object or setting found in one clause. Name an object such as a house, tree or lake, or ask for night, rain or snow.)
- **S45** “Place a pair of flowers in each of red and yellow.” — expected `[{"action": "add", "type": "flower", "count": 2, "color": "red"}, {"action": "add", "type": "flower", "count": 2, "color": "yellow"}]`, got `[{"action": "add", "type": "flower", "count": 2, "color": null}]` (**no notice: a silent misparse**)
- **S46** “Add flowers in pink and white, four of each.” — expected `[{"action": "add", "type": "flower", "count": 4, "color": "pink"}, {"action": "add", "type": "flower", "count": 4, "color": "white"}]`, got `[]` (An inherited noun group needs an explicit quantity; that object instruction was skipped.)
- **S47** “Plant ten trees: three pink; the rest green.” — expected `[{"action": "add", "type": "tree", "count": 3, "color": "pink"}, {"action": "add", "type": "tree", "count": 7, "color": "green"}]`, got `[]` (Partition counts do not match the declared total; that object instruction was skipped.)
- **S48** “Draw two clusters of three flowers.” — expected `[{"action": "add", "type": "flower", "count": 6, "color": null}]`, got `[]` (Skipped flower: specify an unambiguous non-negative whole-number quantity.)
- **S49** “Build three houses, then make two of them red.” — expected `[{"action": "add", "type": "house", "count": 3, "color": null}, {"action": "recolor", "type": "house", "count": 2, "color": "red"}]`, got `[{"action": "add", "type": "house", "count": 3, "color": null}]` (Object pronouns can be removal subjects or spatial landmarks; no object was created from this reference.)
- **S50** “Build twelve houses: a sixth red and the rest blue.” — expected `[{"action": "add", "type": "house", "count": 2, "color": "red"}, {"action": "add", "type": "house", "count": 10, "color": "blue"}]`, got `[{"action": "add", "type": "house", "count": 12, "color": null}]` (**no notice: a silent misparse**)

## What the first run exposed

- **Two silent misparses**: `a pair of flowers in each of red and yellow` created two colorless flowers and `a sixth red and the rest blue` created twelve colorless houses, both with no notice. Both now parse; the class is also guarded: if actions were created, nothing else was reported and a typed color was used by no action, a notice says so (`Add a tower next to a red rock` previously ignored “red” silently).
- Semicolon-separated groups (`three pink; the rest green`) had also failed in round ten; they now partition like commas.

## Fixed after the first run

- **S41** Paint the trees red near the lake.
- **S45** Place a pair of flowers in each of red and yellow.
- **S47** Plant ten trees: three pink; the rest green.
- **S49** Build three houses, then make two of them red.
- **S50** Build twelve houses: a sixth red and the rest blue.

## Still outside the grammar

- **S44** Plant trees in each of pink and white, two per color. — count given after a color list
- **S46** Add flowers in pink and white, four of each. — trailing each-count
- **S48** Draw two clusters of three flowers. — group multiplication

These are tracked as strict expected-failures in `tests/test_filter_fixes.py`, so they stay visible and an accidental fix is noticed.

## Retests after the fixes

These retests use sets the parser has now seen, so they are not accuracy estimates. They show that no earlier set regressed.

| Set | Round eleven | After round-twelve fixes |
|---|---|---|
| heldout | 50/50 | 50/50 |
| fresh_v2 | 48/50 | 48/50 |
| fresh_v3 | 45/50 | 45/50 |
| fresh_v4 | 46/50 | 46/50 |
| fresh_v5 | 47/50 | 47/50 |
| fresh_v6 | 46/50 | 46/50 |
| fresh_v7 | 45/50 | 46/50 |
| fresh_v8 | 44/50 | 45/50 |
| fresh_v9 | 44/50 | 45/50 |
| fresh_v10 | 42/50 | 44/50 |
| fresh_v11 | 50/50 | 50/50 |
| fresh_v12 | — (first run 41/50) | 46/50 |

Earlier sets that changed: fresh_v7 (45 → 46), fresh_v8 (44 → 45), fresh_v9 (44 → 45), fresh_v10 (42 → 44). Each change was checked against its gold label before accepting it.

These are implementation-aware, hand-authored diagnostics, not independent accuracy estimates.
