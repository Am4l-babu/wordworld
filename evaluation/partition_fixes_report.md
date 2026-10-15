# WordWorld counted partitions and attribute fixes — 15 October 2026

**Five saved-set retests: 50/50 (100.0%), 47/50 (94.0%), 45/50 (90.0%), 46/50 (92.0%), 46/50 (92.0%). Sixth fresh set: 41/50 (82.0%).**

J41 (extra default tree), J46 (partitioned roof groups), J43 (passive roof clause), J44 (five total) and J45 (omitted predicate) now pass. No previously passing exact-match cases regressed on the five saved sets. Historical labels and prediction files were preserved.

## Changes

- Comma-separated counted descriptions supply the collection instead of adding a bare noun default first. `trees, two green and three yellow` produces exactly five trees in two groups. Collective alias defaults are also replaced by explicit descriptions.
- When a declared total is followed by relative/part/color descriptions, group counts must sum to it. `two houses, one with a blue roof and one with a green roof` creates two houses; a conflicting total abstains with a notice. Count agreement also disambiguates appositive one/ones groups. Existing explicitly additive and-groups and nonmatching appositive ones additions retain their documented behavior.
- Count-first continuation reading handles one/ones, relative and part clauses, and omitted color predicates. `two trees that are green and three yellow` retains both groups. Explicit next nouns stay separate; quantities are never found by scanning through another noun or placement constraint.
- Passive part clauses support has/have/had been painted/colored/coloured for mapped roofs, leaves/foliage and petals. `five total` joins existing post-noun quantity endings. Negated/conflicting attributes, mismatched totals and missing group quantities abstain with notices.
- Shared source colors remain scoped to partitions. Per-group negation/zero counts, shared placement, exact source spans and reference bindings continue to work. Partition references bind only actual group actions, without a phantom default action. Rule-based grounding and the existing scene schema are unchanged.

## Verification

| Check | Result |
|---|---|
| Python parser/API tests | 322 passed; 42 added cases |
| Original development set | 50/50 exact actions |
| Scene/preview tests | 16 passed |
| Desktop/mobile Chromium | 22 passed |
| React production build | Passed |

The new browser flow checks exactly five new green/yellow trees, two declared houses with distinct blue/purple roofs, five flowers from a trailing total, partition reference placement and undo/redo. Screenshots: `.runtime/partition-fixes-desktop.png` and `.runtime/partition-fixes-mobile.png`. Size descriptors still do not change sprite size; parser evaluation does not measure geometry.

## Evaluation method

The sixth sample has 50 new hand-authored commands, gold actions and scopes frozen before first prediction, with backend source and input hashes. There were no normalized exact overlaps with all six earlier datasets, Python regression literals, browser test literals or README lines at freeze time. Similar grammar is intentional. The author saw the implementation and previous failures; these are diagnostic samples, not independent human-labeled or random real-user accuracy estimates. No backend rules or labels were changed after observing sixth-set predictions.

**Fresh split: 40/40 core, 1/10 broader probes.** Core includes zero/negated groups and one zero-total refusal. Broader gold follows intended English outside the implemented syntax. The 82% overall score must be read with that split. Differing samples are not paired before/after comparisons.

| Set | Previous round | Current round |
|---|---:|---:|
| Saved diagnostic set 1 | 50/50 (100.0%) | 50/50 (100.0%) |
| Saved diagnostic set 2 | 47/50 (94.0%) | 47/50 (94.0%) |
| Saved diagnostic set 3 | 45/50 (90.0%) | 45/50 (90.0%) |
| Saved diagnostic set 4 | 46/50 (92.0%) | 46/50 (92.0%) |
| Saved diagnostic set 5 | 41/50 (82.0%) | 46/50 (92.0%) |
| Sixth fresh 50 | Not previously executed | 41/50 (82.0%) |

| Per-command metric | Set 1 | Set 2 | Set 3 | Set 4 | Set 5 | Fresh 6 |
|---|---:|---:|---:|---:|---:|---:|
| Intent sequence | 50/50 (100.0%) | 47/50 (94.0%) | 45/50 (90.0%) | 47/50 (94.0%) | 47/50 (94.0%) | 43/50 (86.0%) |
| Objects/counts/colors | 50/50 (100.0%) | 48/50 (96.0%) | 46/50 (92.0%) | 47/50 (94.0%) | 47/50 (94.0%) | 43/50 (86.0%) |
| Spatial fields, gold-spatial subset | 22/22 (100.0%) | 18/19 (94.7%) | 18/21 (85.7%) | 12/13 (92.3%) | 7/8 (87.5%) | 8/9 (88.9%) |
| Settings, gold-setting subset | 6/6 (100.0%) | 4/5 (80.0%) | 3/4 (75.0%) | 1/2 (50.0%) | 1/2 (50.0%) | 1/2 (50.0%) |

Exact match compares every field of every ordered action dictionary. Field metrics are per-command sequences, not token scores; the object metric includes matching empty typed-action lists in pure settings. Spatial/settings metrics use gold-bearing subsets.

## Remaining errors

The sixth set has nine errors and no exceptions. Three failures (L41, L42, L50) emit wrong or empty actions without notices.

| Pattern | Cases | Actual behavior |
|---|---|---|
| Colon partitions | L41 | `five houses: two blue and three red` keeps only five default-color houses. |
| Quantity word order | L42 | `a total of five` creates one flower instead of five, without notice. |
| Remainder descriptions | L43 | `the remaining three` is missed, causing a total-mismatch refusal. |
| Passive adverbs | L44 | `has already been painted` abstains. |
| Shared tail after a comma | L45 | `all near the lake` is split off, dropping placement from otherwise correct groups. |
| Latter references | L46 | `two more of the latter` loses the new group. |
| Group multiplication | L47 | `two groups of three` abstains instead of creating six flowers. |
| Subordinate creation | L48 | Preservation swallows `while building two houses`. |
| Time/weather paraphrases | L50 | `daylight without any snow` emits no settings and no notice. |

L49 passes: `a bridge that goes over the stream` produces only a bridge across the river. This verifies that wording, not general finite-clause understanding. The saved sets retain sixteen errors, all listed below.

## All 50 fresh commands

| ID | Scope | Result | Command |
|---|---|---|---|
| L01 | core | PASS | Plant trees, three green and two purple. |
| L02 | core | PASS | Build houses, two with orange roofs and three with white roofs. |
| L03 | core | PASS | Create flowers, four pink ones and two yellow ones. |
| L04 | core | PASS | Place six cottages, two with blue roofs and four with green roofs. |
| L05 | core | PASS | Add flowers, three whose petals are red and one whose petals are purple. |
| L06 | core | PASS | Build four houses, one whose roof has been painted orange and three white. |
| L07 | core | PASS | Plant blue trees, two small ones and one large one. |
| L08 | core | PASS | Add trees, zero purple and four green. |
| L09 | core | PASS | Add trees, not one pink and two white. |
| L10 | core | PASS | Draw flowers, one blue and one purple near the lake. |
| L11 | core | PASS | Create houses, two that are white, three that are yellow, and one pink. |
| L12 | core | PASS | Add three houses, three with pink roofs. |
| L13 | core | PASS | Build two houses whose roofs have been painted orange. |
| L14 | core | PASS | Place a cottage with a roof which has been coloured purple. |
| L15 | core | PASS | Add a home with a roof that had been colored blue. |
| L16 | core | PASS | Create a house whose roof has been painted green near the river. |
| L17 | core | PASS | Plant two trees with leaves which have been coloured pink. |
| L18 | core | PASS | Place flowers whose petals have been colored red. |
| L19 | core | PASS | Add a house with a roof which had been painted yellow and two with roofs that have been painted white. |
| L20 | core | PASS | Add a house with a roof that has been painted white and three blue ones. |
| L21 | core | PASS | Add rocks, eight total. |
| L22 | core | PASS | Build cottages, exactly four total. |
| L23 | core | PASS | Plant trees, half a dozen total. |
| L24 | core | PASS | Create towers, two pairs total. |
| L25 | core | PASS | Add flowers, twenty-five total. |
| L26 | core | PASS | Draw roads, exactly zero total. |
| L27 | core | PASS | Add bridges, three total over the stream. |
| L28 | core | PASS | Place mountains, five total behind the castle. |
| L29 | core | PASS | Plant one tree that is blue and two pink and three white. |
| L30 | core | PASS | Build two houses with green roofs and four orange. |
| L31 | core | PASS | Add two flowers that are purple and not three pink. |
| L32 | core | PASS | Build three small houses and two blue near the pond. |
| L33 | core | PASS | Add two flowers that are yellow and one purple; remove them. |
| L34 | core | PASS | Build houses, one blue and one green; put a rock between them. |
| L35 | core | PASS | Place two cottages, one with a yellow roof and one with an orange roof; remove them. |
| L36 | core | PASS | Plant trees, two green and three pink; remove four of them; remove it. |
| L37 | core | PASS | Keep the lake; add flowers, exactly three total; make it night. |
| L38 | core | PASS | Behind the tower, plant trees, one blue and two purple. |
| L39 | core | PASS | Don’t build a house whose roof has been painted red; add a tree. |
| L40 | core | PASS | Reset; build houses, two with pink roofs and three with white roofs; remove them. |
| L41 | capability_probe | FAIL | Build five houses: two blue and three red. |
| L42 | capability_probe | FAIL | Add flowers, a total of five. |
| L43 | capability_probe | FAIL | Plant five trees, two green and the remaining three yellow. |
| L44 | capability_probe | FAIL | Build a house whose roof has already been painted blue. |
| L45 | capability_probe | FAIL | Build five houses, two blue, three red, all near the lake. |
| L46 | capability_probe | FAIL | Plant trees, two green, three pink; add two more of the latter. |
| L47 | capability_probe | FAIL | Create two groups of three yellow flowers. |
| L48 | capability_probe | FAIL | Leave the trees untouched while building two houses. |
| L49 | capability_probe | PASS | Build a bridge that goes over the stream. |
| L50 | capability_probe | FAIL | Make it daylight without any snow. |

## Sixth-set failures

### L41: Build five houses: two blue and three red.

Expected:

```json
[
  {
    "action": "add",
    "type": "house",
    "count": 2,
    "color": "blue"
  },
  {
    "action": "add",
    "type": "house",
    "count": 3,
    "color": "red"
  }
]
```

Actual:

```json
[
  {
    "action": "add",
    "type": "house",
    "count": 5,
    "color": null
  }
]
```

Notices: None.

### L42: Add flowers, a total of five.

Expected:

```json
[
  {
    "action": "add",
    "type": "flower",
    "count": 5,
    "color": null
  }
]
```

Actual:

```json
[
  {
    "action": "add",
    "type": "flower",
    "count": 1,
    "color": null
  }
]
```

Notices: None.

### L43: Plant five trees, two green and the remaining three yellow.

Expected:

```json
[
  {
    "action": "add",
    "type": "tree",
    "count": 2,
    "color": "green"
  },
  {
    "action": "add",
    "type": "tree",
    "count": 3,
    "color": "yellow"
  }
]
```

Actual:

```json
[]
```

Notices: Partition counts do not match the declared total; that object instruction was skipped.

### L44: Build a house whose roof has already been painted blue.

Expected:

```json
[
  {
    "action": "add",
    "type": "house",
    "count": 1,
    "color": "blue"
  }
]
```

Actual:

```json
[]
```

Notices: Unsupported, negated or ambiguous post-noun color; that object instruction was skipped.

### L45: Build five houses, two blue, three red, all near the lake.

Expected:

```json
[
  {
    "action": "add",
    "type": "house",
    "count": 2,
    "color": "blue",
    "relation": "near",
    "target": "lake"
  },
  {
    "action": "add",
    "type": "house",
    "count": 3,
    "color": "red",
    "relation": "near",
    "target": "lake"
  }
]
```

Actual:

```json
[
  {
    "action": "add",
    "type": "house",
    "count": 2,
    "color": "blue"
  },
  {
    "action": "add",
    "type": "house",
    "count": 3,
    "color": "red"
  }
]
```

Notices: Skipped a context-only or unsupported instruction; use an explicit add/build/plant verb to create objects.

### L46: Plant trees, two green, three pink; add two more of the latter.

Expected:

```json
[
  {
    "action": "add",
    "type": "tree",
    "count": 2,
    "color": "green"
  },
  {
    "action": "add",
    "type": "tree",
    "count": 3,
    "color": "pink"
  },
  {
    "action": "add",
    "type": "tree",
    "count": 2,
    "color": "pink"
  }
]
```

Actual:

```json
[
  {
    "action": "add",
    "type": "tree",
    "count": 2,
    "color": "green"
  },
  {
    "action": "add",
    "type": "tree",
    "count": 3,
    "color": "pink"
  }
]
```

Notices: No supported object or setting found in one clause. Name an object explicitly; pronoun references are not resolved.

### L47: Create two groups of three yellow flowers.

Expected:

```json
[
  {
    "action": "add",
    "type": "flower",
    "count": 6,
    "color": "yellow"
  }
]
```

Actual:

```json
[]
```

Notices: Skipped flower: specify an unambiguous non-negative whole-number quantity.

### L48: Leave the trees untouched while building two houses.

Expected:

```json
[
  {
    "action": "add",
    "type": "house",
    "count": 2,
    "color": null
  }
]
```

Actual:

```json
[]
```

Notices: Preserved referenced objects; no creation or removal was applied for that clause.

### L50: Make it daylight without any snow.

Expected:

```json
[
  {
    "action": "setting",
    "key": "time",
    "value": "day"
  },
  {
    "action": "setting",
    "key": "weather",
    "value": "clear"
  }
]
```

Actual:

```json
[]
```

Notices: None.


## Saved set 2 remaining failures

### F35: Do not make it midnight; make it daylight.

Expected:

```json
[
  {
    "action": "setting",
    "key": "time",
    "value": "day"
  }
]
```

Actual:

```json
[]
```

Notices: Skipped a negated instruction; no objects were changed for that clause.; Object pronouns can be removal subjects or spatial landmarks; no object was created from this reference.

### F48: Leave the houses untouched while adding a lake.

Expected:

```json
[
  {
    "action": "add",
    "type": "lake",
    "count": 1,
    "color": null
  }
]
```

Actual:

```json
[]
```

Notices: Preserved referenced objects; no creation or removal was applied for that clause.

### F50: Construct two red cottages next to the pond.

Expected:

```json
[
  {
    "action": "add",
    "type": "house",
    "count": 2,
    "color": "red",
    "relation": "near",
    "target": "lake"
  }
]
```

Actual:

```json
[]
```

Notices: Skipped a context-only or unsupported instruction; use an explicit add/build/plant verb to create objects.


## Saved set 3 remaining failures

### G43: Build a bridge that crosses the river.

Expected:

```json
[
  {
    "action": "add",
    "type": "bridge",
    "count": 1,
    "color": null,
    "relation": "across",
    "target": "river"
  }
]
```

Actual:

```json
[]
```

Notices: Unsupported connection between object nouns; that object instruction was skipped instead of creating its landmark.

### G44: Construct three white homes near the river.

Expected:

```json
[
  {
    "action": "add",
    "type": "house",
    "count": 3,
    "color": "white",
    "relation": "near",
    "target": "river"
  }
]
```

Actual:

```json
[]
```

Notices: Skipped a context-only or unsupported instruction; use an explicit add/build/plant verb to create objects.

### G45: Keep the trees untouched while building a house.

Expected:

```json
[
  {
    "action": "add",
    "type": "house",
    "count": 1,
    "color": null
  }
]
```

Actual:

```json
[]
```

Notices: Preserved referenced objects; no creation or removal was applied for that clause.

### G46: Make it day without any rain.

Expected:

```json
[
  {
    "action": "setting",
    "key": "time",
    "value": "day"
  },
  {
    "action": "setting",
    "key": "weather",
    "value": "clear"
  }
]
```

Actual:

```json
[
  {
    "action": "setting",
    "key": "time",
    "value": "day"
  }
]
```

Notices: None.

### G47: Add a house to the east side of the lake.

Expected:

```json
[
  {
    "action": "add",
    "type": "house",
    "count": 1,
    "color": null,
    "relation": "right",
    "target": "lake"
  }
]
```

Actual:

```json
[]
```

Notices: Unsupported connection between object nouns; that object instruction was skipped instead of creating its landmark.


## Saved set 4 remaining failures

### H45: Build houses in two groups of three.

Expected:

```json
[
  {
    "action": "add",
    "type": "house",
    "count": 6,
    "color": null
  }
]
```

Actual:

```json
[
  {
    "action": "add",
    "type": "house",
    "count": 1,
    "color": null
  }
]
```

Notices: None.

### H48: Build a house to the northern side of the pond.

Expected:

```json
[
  {
    "action": "add",
    "type": "house",
    "count": 1,
    "color": null,
    "relation": "above",
    "target": "lake"
  }
]
```

Actual:

```json
[]
```

Notices: Unsupported connection between object nouns; that object instruction was skipped instead of creating its landmark.

### H49: Preserve the cottage while planting three trees.

Expected:

```json
[
  {
    "action": "add",
    "type": "tree",
    "count": 3,
    "color": null
  }
]
```

Actual:

```json
[]
```

Notices: Preserved referenced objects; no creation or removal was applied for that clause.

### H50: Make it sunny with no precipitation.

Expected:

```json
[
  {
    "action": "setting",
    "key": "time",
    "value": "day"
  },
  {
    "action": "setting",
    "key": "weather",
    "value": "clear"
  }
]
```

Actual:

```json
[
  {
    "action": "setting",
    "key": "time",
    "value": "day"
  }
]
```

Notices: None.


## Saved set 5 remaining failures

### J47: Build two cottages near the lake; add three large ones behind the tower.

Expected:

```json
[
  {
    "action": "add",
    "type": "house",
    "count": 2,
    "color": null,
    "relation": "near",
    "target": "lake"
  },
  {
    "action": "add",
    "type": "house",
    "count": 3,
    "color": null,
    "relation": "above",
    "target": "tower"
  }
]
```

Actual:

```json
[
  {
    "action": "add",
    "type": "house",
    "count": 2,
    "color": null,
    "relation": "near",
    "target": "lake"
  }
]
```

Notices: An inherited noun after a placement or new verb needs an explicit source noun; its landmark was not created.; Could not resolve an inherited noun outside an adjacent creation group; use an explicit object noun.

### J48: Create castles in three groups of two.

Expected:

```json
[
  {
    "action": "add",
    "type": "castle",
    "count": 6,
    "color": null
  }
]
```

Actual:

```json
[
  {
    "action": "add",
    "type": "castle",
    "count": 1,
    "color": null
  }
]
```

Notices: None.

### J49: Keep the flowers while adding two blue houses.

Expected:

```json
[
  {
    "action": "add",
    "type": "house",
    "count": 2,
    "color": "blue"
  }
]
```

Actual:

```json
[]
```

Notices: Preserved referenced objects; no creation or removal was applied for that clause.

### J50: Make it daylight and stop the snow.

Expected:

```json
[
  {
    "action": "setting",
    "key": "time",
    "value": "day"
  },
  {
    "action": "setting",
    "key": "weather",
    "value": "clear"
  }
]
```

Actual:

```json
[
  {
    "action": "setting",
    "key": "weather",
    "value": "clear"
  }
]
```

Notices: None.

## Reproduce

From the root:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests
.\.venv\Scripts\python.exe -m tests.evaluate
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --allow-parser-change --output evaluation/heldout_retest_v6.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v2.json --dataset-sha256 050f1f92dba55b89883ebd05c4dc074b287c230a65f33f3d12a7a321ee17042b --allow-parser-change --output evaluation/fresh_v2_retest_v6.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v3.json --dataset-sha256 bc902a965baba135a0b81dc0774230921ed49a82bb510305a771da0e1a684927 --allow-parser-change --output evaluation/fresh_v3_retest_v6.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v4.json --dataset-sha256 83f280f866430ebcabf50de1ac3741a62da42d74757f20fb97db2c675c62a0cd --allow-parser-change --output evaluation/fresh_v4_retest_v6.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v5.json --dataset-sha256 e20bbe0ba47f12431c33708b4aa653ce8689a2b9027aca7294747dc0c0f9bc8e --allow-parser-change --output evaluation/fresh_v5_retest_v6.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v6.json --dataset-sha256 b4c823eafa84322f3c164fcaa0080bf5ed4f94f61d374c8dcd2145c74fed3703 --output evaluation/fresh_results_v6.json
.\.venv\Scripts\python.exe -X utf8 -m evaluation.write_partition_report
```

From `frontend/`: `npm test`, `npm run test:e2e` (local servers running), `npm run build`.

Labels: `tests/fresh_commands_v6.json`. Predictions/notices: `evaluation/fresh_results_v6.json`. Regressions: `tests/test_partition_fixes.py`, `frontend/tests/browser/smoke.spec.js`.

Parser SHA256: `2a9f0ce3d09d21c993863504216a0283fc1c22496edc9cd65647df76a8ce5359`.
Backend pipeline SHA256: `34f1a1013de988362e5b1f78197424fb5b2e414497fe294e4d2554d2b3979d6f`.
Sixth dataset SHA256: `b4c823eafa84322f3c164fcaa0080bf5ed4f94f61d374c8dcd2145c74fed3703`.

All six evaluations verified the same backend fingerprint before and after prediction. Once this sample informs future rule changes, use separate retest outputs and a new frozen sample for another fresh-command claim.
