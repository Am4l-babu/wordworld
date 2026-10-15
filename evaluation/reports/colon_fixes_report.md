# WordWorld colon, total-of and remainder fixes — 15 October 2026

**Six saved-set retests: 50/50 (100.0%), 47/50 (94.0%), 45/50 (90.0%), 46/50 (92.0%), 46/50 (92.0%), 44/50 (88.0%). Seventh fresh set: 40/50 (80.0%).**

L41 (colon partition), L42 (a total of five) and L43 (the remaining three) now pass. Set six improves from 41/50 to 44/50; no previously passing case regressed on any of the six saved sets. Historical gold and predictions remain unchanged.

## Changes

- Colon-separated counted descriptions replace the noun default. Declared totals must equal the group sum, including one/ones groups. Shared source colors and original text offsets are retained.
- Adjacent `a/the total of` quantities are anchored to the following number phrase, including exactly, pairs and dozen. Invalid, missing, negative, fractional, ambiguous or conflicting counts abstain. Existing per-action cap remains 16.
- Explicitly counted `(the) remaining` groups require a declared total, must be unique and last, and must agree with total arithmetic. No implicit remainder is inferred for `the rest`. Successful groups participate in references without phantom default objects.
- README command URLs safely prefill the editor without executing a request or resetting saved objects. The README includes a real animated recording, static poster, example links, native expandable guides and the existing Vercel full-stack preview.

## Verification

| Check | Result |
|---|---|
| Python parser/API tests | 360 passed; 38 new regressions |
| Original development set | 50/50 exact actions |
| Scene/preview tests | 16 passed |
| Local desktop/mobile Chromium | 26 passed |
| React production build | Passed |

Browser checks verify colon groups, total-of counts, remainder highlights, actual scene colors/counts, safe URL input, markup isolation and oversized-query refusal. Existing editing, undo, references, API errors and mobile checks remain green. README captures come from the full local spaCy-backed API; the GIF is five actual scene states, not an illustration of unimplemented behavior.

## Evaluation method

All 50 new command strings, expected action dictionaries and 40 core/10 capability-probe scopes were frozen before the first parser call. Backend and development-input SHA256 fingerprints are embedded in the dataset. A normalized exact-overlap check included all seven earlier datasets, Python test literals, browser smoke/capture literals, README/archive lines and decoded example URLs. Similar grammar is intentional; semantic independence is not claimed.

The author saw the implementation and earlier failures. These are hand-authored diagnostic samples, not independent human-labeled or random real-user accuracy estimates. No backend rules or gold labels were changed after seventh-set predictions. Once these examples inform future changes, treat them as regressions and freeze another new sample.

**Fresh split: 40/40 core and 0/10 broader probes. Overall: 40/50 (80%).** Ten core cases expect no action for zero, invalid, ambiguous or inconsistent counts. Other cases mix valid groups with zero/negated groups. The core score must be read in that context. Different fresh samples are not paired before/after measurements.

| Set | Before this round | Current round |
|---|---:|---:|
| Saved diagnostic set 1 | 50/50 (100.0%) | 50/50 (100.0%) |
| Saved diagnostic set 2 | 47/50 (94.0%) | 47/50 (94.0%) |
| Saved diagnostic set 3 | 45/50 (90.0%) | 45/50 (90.0%) |
| Saved diagnostic set 4 | 46/50 (92.0%) | 46/50 (92.0%) |
| Saved diagnostic set 5 | 46/50 (92.0%) | 46/50 (92.0%) |
| Saved diagnostic set 6 | 41/50 (82.0%) | 44/50 (88.0%) |
| Seventh fresh 50 | Not previously executed | 40/50 (80.0%) |

| Per-command metric | Set 1 | Set 2 | Set 3 | Set 4 | Set 5 | Set 6 | Fresh 7 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Intent sequence | 50/50 (100.0%) | 47/50 (94.0%) | 45/50 (90.0%) | 47/50 (94.0%) | 47/50 (94.0%) | 45/50 (90.0%) | 41/50 (82.0%) |
| Objects/counts/colors | 50/50 (100.0%) | 48/50 (96.0%) | 46/50 (92.0%) | 47/50 (94.0%) | 47/50 (94.0%) | 46/50 (92.0%) | 42/50 (84.0%) |
| Spatial, gold-spatial subset | 22/22 (100.0%) | 18/19 (94.7%) | 18/21 (85.7%) | 12/13 (92.3%) | 7/8 (87.5%) | 8/9 (88.9%) | 6/7 (85.7%) |
| Settings, gold-setting subset | 6/6 (100.0%) | 4/5 (80.0%) | 3/4 (75.0%) | 1/2 (50.0%) | 1/2 (50.0%) | 1/2 (50.0%) | 1/2 (50.0%) |

Exact match compares every field of every ordered action dictionary. Field metrics compare per-command sequences, not tokens. The object metric includes empty typed-action lists for settings-only cases; spatial and setting metrics use gold-bearing subsets. Parser scores do not measure placement geometry.

## Main remaining NLP errors

All ten broader seventh-set probes fail; no parser exceptions occurred. Two silently emit wrong actions without notices (M43 and M50). The six saved sets retain 22 failures in total.

| Pattern | Case | Actual behavior |
|---|---|---|
| Implicit remainder | M41 | `the rest green` is not counted; refuses the inconsistent partition. |
| Total inside a part phrase | M42 | `with a total of five roofs` abstains. |
| Distributive quantity | M43 | `three each of pink and white` emits six default-colored flowers, without notice. |
| Semicolon continuation | M44 | Semicolon ends the group scope; refuses instead of linking the remainder. |
| Adverb in a passive clause | M45 | `has recently been coloured` abstains. |
| Shared tail after a comma | M46 | Creates the right groups but drops `all beside the river`, with notice. |
| Latter reference | M47 | Creates the first groups, omits the additional latter object, with notice. |
| Multiplicative groups | M48 | `three rows of two` abstains rather than multiplying. |
| Subordinate creation | M49 | Preservation swallows `while planting...`, with notice. |
| Negated setting paraphrase | M50 | `turn off the rain` incorrectly enables rain; daylight is ignored; no notice. |

Prioritize M50 and M43 because their wrong actions are silent, followed by shared modifier scope and implicit remainders. Full predictions and notices below separate refusal from partial or incorrect execution.

## All 50 fresh commands

| ID | Scope | Result | Command |
|---|---|---|---|
| M01 | core | PASS | Create seven cottages: three orange and four white. |
| M02 | core | PASS | Plant flowers: two purple, three pink, and one yellow. |
| M03 | core | PASS | Draw four trees: one with blue leaves and three with green leaves. |
| M04 | core | PASS | Build six homes: two whose roofs are pink and four whose roofs are yellow. |
| M05 | core | PASS | Place five blue flowers: two small ones and three large ones. |
| M06 | core | PASS | Build four houses with white roofs: one small one and three large ones. |
| M07 | core | PASS | Plant three trees: zero yellow and three purple. |
| M08 | core | PASS | Place trees: not two white and four green. |
| M09 | core | PASS | Draw three flowers: one orange and two pink beside the pond. |
| M10 | core | PASS | To the left of the castle, build four houses: one white and three yellow. |
| M11 | core | PASS | Create trees, a total of eight. |
| M12 | core | PASS | Place bridges, a total of exactly two across the creek. |
| M13 | core | PASS | Build cottages, the total of three. |
| M14 | core | PASS | Draw rocks: a total of a dozen. |
| M15 | core | PASS | Add mountains, a total of half a dozen behind the tower. |
| M16 | core | PASS | Create flowers, a total of two pairs. |
| M17 | core | PASS | Place roads, a total of nineteen. |
| M18 | core | PASS | Draw towers, a total of zero. |
| M19 | core | PASS | Place castles, a total of -2. |
| M20 | core | PASS | Build homes, a total of 2.5. |
| M21 | core | PASS | Plant flowers, a total of four or seven. |
| M22 | core | PASS | Add rocks, never a total of six. |
| M23 | core | PASS | Create flowers, a total of six: two yellow and four orange. |
| M24 | core | PASS | Build houses, a total of seven: four red and the remaining three white. |
| M25 | core | PASS | Plant eight trees, three purple and the remaining five green. |
| M26 | core | PASS | Create six flowers: one red, two yellow, and the remaining three pink. |
| M27 | core | PASS | Build four cottages: one with a green roof and remaining three with orange roofs. |
| M28 | core | PASS | Plant three blue trees: one small one and the remaining two large ones. |
| M29 | core | PASS | Add two white flowers: two small ones and remaining zero large ones. |
| M30 | core | PASS | Near the river, place five houses: one purple and the remaining four blue. |
| M31 | core | PASS | Build houses, a total of two: one red and the remaining one pink; put a tower between them. |
| M32 | core | PASS | Create four trees: one white and remaining three blue; remove two of them; remove them. |
| M33 | core | PASS | Clear the world; place flowers, a total of three: one yellow and the remaining two purple; remove them. |
| M34 | core | PASS | Keep the castle; draw rocks, a total of four; make it snow. |
| M35 | core | PASS | Do not build six cottages: two red and the remaining four blue; plant a flower. |
| M36 | core | PASS | Build seven houses: two pink and the remaining four white. |
| M37 | core | PASS | Plant flowers: two yellow and the remaining three green. |
| M38 | core | PASS | Create five trees: remaining two green and three orange. |
| M39 | core | PASS | Build four houses: one red and remaining one blue and remaining two green. |
| M40 | core | PASS | Place three houses: four large ones. |
| M41 | capability_probe | FAIL | Plant seven trees: two purple and the rest green. |
| M42 | capability_probe | FAIL | Build houses with a total of five roofs painted blue. |
| M43 | capability_probe | FAIL | Place six flowers: three each of pink and white. |
| M44 | capability_probe | FAIL | Create four cottages: one red; the remaining three blue. |
| M45 | capability_probe | FAIL | Add a cottage whose roof has recently been coloured orange. |
| M46 | capability_probe | FAIL | Plant four trees: one green and three blue, all beside the river. |
| M47 | capability_probe | FAIL | Build cottages, two yellow and one pink; add another of the latter. |
| M48 | capability_probe | FAIL | Create three rows of two purple trees. |
| M49 | capability_probe | FAIL | Keep the lake unchanged while planting three pink flowers. |
| M50 | capability_probe | FAIL | Bring back daylight and turn off the rain. |

## Seventh-set failures

### M41: Plant seven trees: two purple and the rest green.

Expected:

```json
[
  {
    "action": "add",
    "type": "tree",
    "count": 2,
    "color": "purple"
  },
  {
    "action": "add",
    "type": "tree",
    "count": 5,
    "color": "green"
  }
]
```

Actual:

```json
[]
```

Notices: Partition counts do not match the declared total; that object instruction was skipped.

### M42: Build houses with a total of five roofs painted blue.

Expected:

```json
[
  {
    "action": "add",
    "type": "house",
    "count": 5,
    "color": "blue"
  }
]
```

Actual:

```json
[]
```

Notices: Unsupported, negated or ambiguous post-noun color; that object instruction was skipped.

### M43: Place six flowers: three each of pink and white.

Expected:

```json
[
  {
    "action": "add",
    "type": "flower",
    "count": 3,
    "color": "pink"
  },
  {
    "action": "add",
    "type": "flower",
    "count": 3,
    "color": "white"
  }
]
```

Actual:

```json
[
  {
    "action": "add",
    "type": "flower",
    "count": 6,
    "color": null
  }
]
```

Notices: None.

### M44: Create four cottages: one red; the remaining three blue.

Expected:

```json
[
  {
    "action": "add",
    "type": "house",
    "count": 1,
    "color": "red"
  },
  {
    "action": "add",
    "type": "house",
    "count": 3,
    "color": "blue"
  }
]
```

Actual:

```json
[]
```

Notices: Partition counts do not match the declared total; that object instruction was skipped.; No supported object or setting found in one clause. Name an object explicitly; pronoun references are not resolved.

### M45: Add a cottage whose roof has recently been coloured orange.

Expected:

```json
[
  {
    "action": "add",
    "type": "house",
    "count": 1,
    "color": "orange"
  }
]
```

Actual:

```json
[]
```

Notices: Unsupported, negated or ambiguous post-noun color; that object instruction was skipped.

### M46: Plant four trees: one green and three blue, all beside the river.

Expected:

```json
[
  {
    "action": "add",
    "type": "tree",
    "count": 1,
    "color": "green",
    "relation": "near",
    "target": "river"
  },
  {
    "action": "add",
    "type": "tree",
    "count": 3,
    "color": "blue",
    "relation": "near",
    "target": "river"
  }
]
```

Actual:

```json
[
  {
    "action": "add",
    "type": "tree",
    "count": 1,
    "color": "green"
  },
  {
    "action": "add",
    "type": "tree",
    "count": 3,
    "color": "blue"
  }
]
```

Notices: Skipped a context-only or unsupported instruction; use an explicit add/build/plant verb to create objects.

### M47: Build cottages, two yellow and one pink; add another of the latter.

Expected:

```json
[
  {
    "action": "add",
    "type": "house",
    "count": 2,
    "color": "yellow"
  },
  {
    "action": "add",
    "type": "house",
    "count": 1,
    "color": "pink"
  },
  {
    "action": "add",
    "type": "house",
    "count": 1,
    "color": "pink"
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
    "color": "yellow"
  },
  {
    "action": "add",
    "type": "house",
    "count": 1,
    "color": "pink"
  }
]
```

Notices: No supported object or setting found in one clause. Name an object explicitly; pronoun references are not resolved.

### M48: Create three rows of two purple trees.

Expected:

```json
[
  {
    "action": "add",
    "type": "tree",
    "count": 6,
    "color": "purple"
  }
]
```

Actual:

```json
[]
```

Notices: Skipped tree: specify an unambiguous non-negative whole-number quantity.

### M49: Keep the lake unchanged while planting three pink flowers.

Expected:

```json
[
  {
    "action": "add",
    "type": "flower",
    "count": 3,
    "color": "pink"
  }
]
```

Actual:

```json
[]
```

Notices: Preserved referenced objects; no creation or removal was applied for that clause.

### M50: Bring back daylight and turn off the rain.

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
    "value": "rain"
  }
]
```

Notices: None.


## Saved set 2 failures

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


## Saved set 3 failures

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


## Saved set 4 failures

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


## Saved set 5 failures

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


## Saved set 6 failures

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

## Reproduce

From the root (use new output names to preserve historical evidence):

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests
.\.venv\Scripts\python.exe -m tests.evaluate
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/heldout_commands.json --dataset-sha256 d372d2d85208319439929068902779ba4ea9144722caea783a8c792bcbd7a224 --allow-parser-change --output evaluation/results/heldout_retest_v7.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v2.json --dataset-sha256 050f1f92dba55b89883ebd05c4dc074b287c230a65f33f3d12a7a321ee17042b --allow-parser-change --output evaluation/results/fresh_v2_retest_v7.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v3.json --dataset-sha256 bc902a965baba135a0b81dc0774230921ed49a82bb510305a771da0e1a684927 --allow-parser-change --output evaluation/results/fresh_v3_retest_v7.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v4.json --dataset-sha256 83f280f866430ebcabf50de1ac3741a62da42d74757f20fb97db2c675c62a0cd --allow-parser-change --output evaluation/results/fresh_v4_retest_v7.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v5.json --dataset-sha256 e20bbe0ba47f12431c33708b4aa653ce8689a2b9027aca7294747dc0c0f9bc8e --allow-parser-change --output evaluation/results/fresh_v5_retest_v7.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v6.json --dataset-sha256 b4c823eafa84322f3c164fcaa0080bf5ed4f94f61d374c8dcd2145c74fed3703 --allow-parser-change --output evaluation/results/fresh_v6_retest_v7.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v7.json --dataset-sha256 b1c66ed63c5747d59c87b9baaf37f923307cf9d1d42868e7bfeb1ef3fef4b85e --output evaluation/results/fresh_results_v7.json
.\.venv\Scripts\python.exe -X utf8 -m evaluation.scripts.write_colon_report
```

From `frontend/`: `npm test`, `npm run test:e2e` (servers running), `npm run build`.

Frozen labels: `tests/fresh_commands_v7.json`. Predictions/notices: `evaluation/results/fresh_results_v7.json`. New regressions: `tests/test_colon_fixes.py`.

Parser SHA256: `4f0be484acd37ca613d92d8547a1dcc5d86d7de5dccc5fb09f9565fdee686fa5`.
Backend pipeline SHA256: `ada5d384fb6d8a17421095a0481d41b2fc3f143d4670b67d5fa82dfc6f8758aa`.
Seventh dataset SHA256: `b1c66ed63c5747d59c87b9baaf37f923307cf9d1d42868e7bfeb1ef3fef4b85e`.

All seven evaluations verified the same backend fingerprint before and after prediction. Original labels/results have not been overwritten.
