# WordWorld weather, distributive counts, inferred remainders and passive adverbs — 15 October 2026

**Seven saved-set retests: 50/50 (100.0%), 48/50 (96.0%), 45/50 (90.0%), 46/50 (92.0%), 47/50 (94.0%), 45/50 (90.0%), 44/50 (88.0%). Eighth fresh set: 40/50 (80.0%).**

All targeted seventh-set failures pass: M50 (daylight and turn off the rain), M43 (three each), M41 (the rest) and M45 (passive adverb). Seven previously failing commands improve across saved sets, with no previously passing exact match regressing. Historical labels and first-run predictions are preserved.

## Changes

- Weather switches read `turn/switch on/off the rain/snow` and `turn/switch the rain/snow on/off` before weather keywords. Negated switches abstain instead of clearing/enabling weather. Coordinated switches preserve execution order. `daylight` maps to day, completing the previously observed mixed setting command.
- One explicit count distributes across an adjacent list of two or more supported colors, before or after the object noun. `six flowers: three each of pink and white` creates two groups of three, with no default group. Commas inside the list stay in the noun phrase; counts, totals, negatives, zero groups, locations and references use the existing checks. Unknown/ambiguous colors and invalid/missing counts abstain. Highlights deduplicate shared number spans.
- `the rest`, `the remainder` and `the remaining ones` infer total minus prior non-negated groups. A single final remainder and a declared total are required; negative, undefined, repeated, nonfinal or negated inferred remainders abstain. Arithmetic precedes per-action caps, references bind actual group actions, and a zero remainder adds nothing.
- Bounded passive adverbs already/recently/just/newly/previously/freshly work around `been` and before present passive colors. Negation and unsupported modifiers such as almost still abstain. Colors continue mapping to house roofs, tree leaves/foliage and flower petals.
- Deterministic grounding and the action schema are unchanged. spaCy remains responsible for linguistic annotations, not action extraction.

## Verification

| Check | Result |
|---|---|
| Python parser/API suite | 422 passed; 62 added regressions |
| Original development commands | 50/50 exact actions |
| Scene/preview unit tests | 16 passed |
| Desktop/mobile browser suite | 28 passed locally |
| React production build | Passed |

The added browser flow turns rain on then off, checks pink/white distribution counts and stored colors, verifies inferred tree counts and actual SVG foliage colors, checks an orange passive-adverb roof, and exercises undo/redo. Screenshots are in `.runtime/distributive-fixes-desktop.png` and `.runtime/distributive-fixes-mobile.png`.

## Evaluation method

The eighth sample freezes all 50 commands, expected action dictionaries, 40 core/10 broader-probe scopes and backend fingerprints before first prediction. A normalized exact-overlap check covers all eight earlier datasets, Python test literals, browser smoke/capture and UI example literals, README/archive lines and decoded example links. Similar grammar is intentional; semantic independence is not claimed.

The author saw the implementation and earlier failures. These are implementation-aware hand-authored diagnostics, not independent human-labeled or random real-user accuracy estimates. No parser rules or gold labels were changed after eighth-set predictions. Different fresh samples are not paired before/after measurements.

**Fresh: 40/50 (80%), with 40/40 core and 0/10 broader probes.** Nine core commands deliberately expect no actions for invalid/zero/negated inputs. The other 31 core commands expect actual actions. This split limits the meaning of the 100% core score. Geometry, sprite size and cross-request references are not measured.

| Set | Previous round | Current round |
|---|---:|---:|
| Saved diagnostic set 1 | 50/50 (100.0%) | 50/50 (100.0%) |
| Saved diagnostic set 2 | 47/50 (94.0%) | 48/50 (96.0%) |
| Saved diagnostic set 3 | 45/50 (90.0%) | 45/50 (90.0%) |
| Saved diagnostic set 4 | 46/50 (92.0%) | 46/50 (92.0%) |
| Saved diagnostic set 5 | 46/50 (92.0%) | 47/50 (94.0%) |
| Saved diagnostic set 6 | 44/50 (88.0%) | 45/50 (90.0%) |
| Saved diagnostic set 7 | 40/50 (80.0%) | 44/50 (88.0%) |
| Eighth fresh 50 | First execution | 40/50 (80.0%) |

| Per-command metric | Set 1 | Set 2 | Set 3 | Set 4 | Set 5 | Set 6 | Set 7 | Fresh 8 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Intent sequence | 50/50 (100.0%) | 48/50 (96.0%) | 45/50 (90.0%) | 47/50 (94.0%) | 48/50 (96.0%) | 46/50 (92.0%) | 45/50 (90.0%) | 41/50 (82.0%) |
| Objects/counts/colors | 50/50 (100.0%) | 48/50 (96.0%) | 46/50 (92.0%) | 47/50 (94.0%) | 47/50 (94.0%) | 47/50 (94.0%) | 45/50 (90.0%) | 42/50 (84.0%) |
| Spatial, gold-spatial subset | 22/22 (100.0%) | 18/19 (94.7%) | 18/21 (85.7%) | 12/13 (92.3%) | 7/8 (87.5%) | 8/9 (88.9%) | 6/7 (85.7%) | 3/4 (75.0%) |
| Settings, gold-setting subset | 6/6 (100.0%) | 5/5 (100.0%) | 3/4 (75.0%) | 1/2 (50.0%) | 2/2 (100.0%) | 1/2 (50.0%) | 2/2 (100.0%) | 8/9 (88.9%) |

Exact match compares every field of every ordered action dictionary. Field metrics compare per-command sequences, not tokens; the object metric includes empty typed-action lists. Spatial/settings metrics use gold-bearing subsets.

## Main remaining errors

All ten broader eighth-set probes fail; no parser exceptions occurred. N42 silently drops fractional color distribution. N49 incorrectly turns on rain for stop the storm and ignores dawn, although an unrelated pronoun notice appears. Prioritize incorrect execution before adding further paraphrases. The seven saved sets retain 25 failures, all detailed below.

| Pattern | Case | Actual behavior |
|---|---|---|
| Total inside a part phrase | N41 | `with a total of six roofs` abstains. |
| Half-and-half distribution | N42 | Adds eight default-colored flowers; no notice. |
| Shared comma tail | N43 | Drops `all behind the tower`; groups are created without placement, with notice. |
| Semicolon remainder | N44 | Ends partition scope and refuses instead of resolving the rest. |
| Future passive | N45 | `will be painted` abstains. |
| Former reference | N46 | Omits the requested additional group, with notice. |
| Multiplicative groups | N47 | `four clusters of two` abstains. |
| Subordinate creation | N48 | Preservation swallows `while drawing`, with notice. |
| Weather/time paraphrases | N49 | Dawn is ignored and stop the storm enables rain; pronoun notice is unhelpful. |
| Others remainder | N50 | `the others` is unsupported; partition-total mismatch refuses. |

## All 50 fresh commands

| ID | Scope | Result | Command |
|---|---|---|---|
| N01 | core | PASS | Please switch the rain off. |
| N02 | core | PASS | Turn off the snow. |
| N03 | core | PASS | Please switch on rain. |
| N04 | core | PASS | Turn snow off; build a yellow house. |
| N05 | core | PASS | Make it daylight and switch off the rain. |
| N06 | core | PASS | Don’t switch on the snow; plant two green trees. |
| N07 | core | PASS | Make it snow then turn the snow off. |
| N08 | core | PASS | Turn rain on then switch rain off. |
| N09 | core | PASS | Draw eight flowers: four each of red and white. |
| N10 | core | PASS | Plant trees: one each of orange, purple, and green. |
| N11 | core | PASS | Place two each of blue and white houses. |
| N12 | core | PASS | Add flowers, a pair each of purple and orange. |
| N13 | core | PASS | Build six homes: three each of green and pink beside the pond. |
| N14 | core | PASS | Add flowers: no two each of pink and blue. |
| N15 | core | PASS | Create zero each of yellow and blue flowers. |
| N16 | core | PASS | Plant trees: half a dozen each of blue and white. |
| N17 | core | PASS | Build nine houses: three each of purple, orange and yellow; remove them. |
| N18 | core | PASS | Draw five flowers: two each of pink and green. |
| N19 | core | PASS | Place six flowers: four orange and the rest pink. |
| N20 | core | PASS | Build seven houses, two blue and the remainder purple. |
| N21 | core | PASS | Plant eight blue trees: three small ones and the rest large ones. |
| N22 | core | PASS | Create flowers, a total of eight: three purple and the remaining ones white. |
| N23 | core | PASS | Build two cottages: one orange and the rest white; place a rock between them. |
| N24 | core | PASS | Plant four trees: one yellow and the rest pink; remove two of them; remove them. |
| N25 | core | PASS | Place three flowers: three blue and the rest white. |
| N26 | core | PASS | Create trees: one orange and the remainder green. |
| N27 | core | PASS | Build two cottages: three red and the remaining ones white. |
| N28 | core | PASS | Place six flowers: the rest pink and two purple. |
| N29 | core | PASS | Plant seven trees: one blue, the rest green, and the remainder yellow. |
| N30 | core | PASS | Switch off snow; build five homes: two purple and the rest yellow. |
| N31 | core | PASS | Build two houses whose roofs have recently been painted green. |
| N32 | core | PASS | Place a cottage whose roof has already been coloured purple. |
| N33 | core | PASS | Plant three trees whose leaves have just been colored orange. |
| N34 | core | PASS | Create two flowers whose petals are newly painted pink. |
| N35 | core | PASS | Build homes with roofs that had previously been painted blue. |
| N36 | core | PASS | Add flowers with petals which are freshly painted yellow. |
| N37 | core | PASS | Build four homes: one whose roof has already been painted blue and the rest whose roofs have recently been painted red. |
| N38 | core | PASS | Place a house whose roof has not recently been painted orange. |
| N39 | core | PASS | Create a stone whose roof has already been coloured yellow. |
| N40 | core | PASS | Behind the lake, build two houses whose roofs have been freshly painted white. |
| N41 | capability_probe | FAIL | Build cottages with a total of six roofs painted purple. |
| N42 | capability_probe | FAIL | Add eight flowers: half pink and half white. |
| N43 | capability_probe | FAIL | Plant trees: two green and three purple, all behind the tower. |
| N44 | capability_probe | FAIL | Create five houses: two orange; the rest white. |
| N45 | capability_probe | FAIL | Build a house whose roof will be painted pink. |
| N46 | capability_probe | FAIL | Plant trees, one yellow and two green; add one more of the former. |
| N47 | capability_probe | FAIL | Create four clusters of two white flowers. |
| N48 | capability_probe | FAIL | Leave the river untouched while drawing two blue houses. |
| N49 | capability_probe | FAIL | Make it dawn and stop the storm. |
| N50 | capability_probe | FAIL | Build four houses: two with blue roofs and the others green. |

## Eighth-set failures

### N41: Build cottages with a total of six roofs painted purple.

Expected:

```json
[
  {
    "action": "add",
    "type": "house",
    "count": 6,
    "color": "purple"
  }
]
```

Actual:

```json
[]
```

Notices: Unsupported, negated or ambiguous post-noun color; that object instruction was skipped.

### N42: Add eight flowers: half pink and half white.

Expected:

```json
[
  {
    "action": "add",
    "type": "flower",
    "count": 4,
    "color": "pink"
  },
  {
    "action": "add",
    "type": "flower",
    "count": 4,
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
    "count": 8,
    "color": null
  }
]
```

Notices: None.

### N43: Plant trees: two green and three purple, all behind the tower.

Expected:

```json
[
  {
    "action": "add",
    "type": "tree",
    "count": 2,
    "color": "green",
    "relation": "above",
    "target": "tower"
  },
  {
    "action": "add",
    "type": "tree",
    "count": 3,
    "color": "purple",
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
    "type": "tree",
    "count": 2,
    "color": "green"
  },
  {
    "action": "add",
    "type": "tree",
    "count": 3,
    "color": "purple"
  }
]
```

Notices: Skipped a context-only or unsupported instruction; use an explicit add/build/plant verb to create objects.

### N44: Create five houses: two orange; the rest white.

Expected:

```json
[
  {
    "action": "add",
    "type": "house",
    "count": 2,
    "color": "orange"
  },
  {
    "action": "add",
    "type": "house",
    "count": 3,
    "color": "white"
  }
]
```

Actual:

```json
[]
```

Notices: Partition counts do not match the declared total; that object instruction was skipped.; No supported object or setting found in one clause. Name an object explicitly; pronoun references are not resolved.

### N45: Build a house whose roof will be painted pink.

Expected:

```json
[
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
[]
```

Notices: Unsupported, negated or ambiguous post-noun color; that object instruction was skipped.

### N46: Plant trees, one yellow and two green; add one more of the former.

Expected:

```json
[
  {
    "action": "add",
    "type": "tree",
    "count": 1,
    "color": "yellow"
  },
  {
    "action": "add",
    "type": "tree",
    "count": 2,
    "color": "green"
  },
  {
    "action": "add",
    "type": "tree",
    "count": 1,
    "color": "yellow"
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
    "color": "yellow"
  },
  {
    "action": "add",
    "type": "tree",
    "count": 2,
    "color": "green"
  }
]
```

Notices: No supported object or setting found in one clause. Name an object explicitly; pronoun references are not resolved.

### N47: Create four clusters of two white flowers.

Expected:

```json
[
  {
    "action": "add",
    "type": "flower",
    "count": 8,
    "color": "white"
  }
]
```

Actual:

```json
[]
```

Notices: Skipped flower: specify an unambiguous non-negative whole-number quantity.

### N48: Leave the river untouched while drawing two blue houses.

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

### N49: Make it dawn and stop the storm.

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

Notices: Object pronouns can be removal subjects or spatial landmarks; no object was created from this reference.

### N50: Build four houses: two with blue roofs and the others green.

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
    "count": 2,
    "color": "green"
  }
]
```

Actual:

```json
[]
```

Notices: Partition counts do not match the declared total; that object instruction was skipped.


## Saved set 2 failures

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


## Saved set 6 failures

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
[
  {
    "action": "setting",
    "key": "time",
    "value": "day"
  }
]
```

Notices: None.


## Saved set 7 failures

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

## Reproduce

Use separate output names for later retests; preserve historical predictions. From the root:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests
.\.venv\Scripts\python.exe -m tests.evaluate
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/heldout_commands.json --dataset-sha256 d372d2d85208319439929068902779ba4ea9144722caea783a8c792bcbd7a224 --allow-parser-change --output evaluation/results/heldout_retest_v8.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v2.json --dataset-sha256 050f1f92dba55b89883ebd05c4dc074b287c230a65f33f3d12a7a321ee17042b --allow-parser-change --output evaluation/results/fresh_v2_retest_v8.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v3.json --dataset-sha256 bc902a965baba135a0b81dc0774230921ed49a82bb510305a771da0e1a684927 --allow-parser-change --output evaluation/results/fresh_v3_retest_v8.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v4.json --dataset-sha256 83f280f866430ebcabf50de1ac3741a62da42d74757f20fb97db2c675c62a0cd --allow-parser-change --output evaluation/results/fresh_v4_retest_v8.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v5.json --dataset-sha256 e20bbe0ba47f12431c33708b4aa653ce8689a2b9027aca7294747dc0c0f9bc8e --allow-parser-change --output evaluation/results/fresh_v5_retest_v8.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v6.json --dataset-sha256 b4c823eafa84322f3c164fcaa0080bf5ed4f94f61d374c8dcd2145c74fed3703 --allow-parser-change --output evaluation/results/fresh_v6_retest_v8.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v7.json --dataset-sha256 b1c66ed63c5747d59c87b9baaf37f923307cf9d1d42868e7bfeb1ef3fef4b85e --allow-parser-change --output evaluation/results/fresh_v7_retest_v8.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v8.json --dataset-sha256 44e7288480226cbe1597aa5d925fd41b518b43bec82b260104ffe266c4be1dc5 --output evaluation/results/fresh_results_v8.json
.\.venv\Scripts\python.exe -X utf8 -m evaluation.scripts.write_distributive_report
```

From `frontend/`: `npm test`, `npm run build`, `npm run test:e2e` with both servers running. Set `WORDWORLD_BASE_URL` for production browser verification.

Gold: `tests/fresh_commands_v8.json`. Predictions/notices: `evaluation/results/fresh_results_v8.json`. Regressions: `tests/test_distributive_fixes.py`, `frontend/tests/browser/smoke.spec.js`.

Parser SHA256: `f5439a5326181b13a4555648da3217000876d5f8f40051291391831a7290bbbf`.
Backend pipeline SHA256: `d65a3896893a81bafce4b68d0c7c45f8a219732d61dc189817d5e0bb4726fdf9`.
Eighth dataset SHA256: `44e7288480226cbe1597aa5d925fd41b518b43bec82b260104ffe266c4be1dc5`.

All eight evaluations verified the same backend fingerprint before and after prediction. Frozen source hashes match the tested parser; no subsequent rule/gold tuning occurred.
