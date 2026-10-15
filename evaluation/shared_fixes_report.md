# WordWorld storm, half quantities, shared locations and future passive fixes — 15 October 2026

**Eight saved-set retests: 50/50 (100.0%), 48/50 (96.0%), 45/50 (90.0%), 46/50 (92.0%), 47/50 (94.0%), 46/50 (92.0%), 45/50 (90.0%), 44/50 (88.0%). Ninth fresh set: 40/50 (80.0%).**

All four targeted eighth-set errors now pass: N49 (dawn and stop the storm), N42 (half-and-half), N43 (shared comma location) and N45 (future passive). L45 and M46 also improve. No previously passing exact match regressed across the eight saved sets. Historical labels and first-run predictions remain intact.

## Changes

- Stop/end weather phrases are matched before embedded rain/storm words. Negated controls leave weather unchanged and report a notice. Coordinated controls execute in order. Dawn maps to day, completing the observed mixed setting request.
- Adjacent half groups require an explicit even whole-number total and a comma/colon partition. `half pink and half white` divides that total into integer groups. Supports `half of them`, shared colors, part clauses, placement, inferred rest and request-local references. Odd, missing, inconsistent or additive half totals abstain. Arithmetic precedes the existing 16-per-action cap.
- A comma followed by `all` plus a supported location remains attached to the preceding same-noun counted collection. Every group receives the placement, with no extra landmark creation. Missing landmarks, negated constraints and conflicting placements retain refusal behavior. Shared tails across different source noun types remain unsupported.
- Adjacent part clauses accept will/shall be painted/colored/coloured with supported passive adverbs. Negation, unmapped parts and ambiguous colors abstain. Future perfect remains outside this grammar.
- Mobile: the single command editor moves above the island on phones and narrow landscape screens; drafts and scenes survive breakpoint changes. Create has a visible label, Enter inserts a newline on phones, textarea text is 16px, primary touch controls are at least 44 by 44 pixels, help remains available, and the help dialog scrolls within short screens. An explicit canvas width fixes tablet overflow. See [mobile QA](../docs/MOBILE_QA.md) for screenshots and limits.

## Verification

| Check | Result |
|---|---|
| Python parser/API suite | 466 passed; 44 added regressions |
| Original development commands | 50/50 exact actions |
| Scene/preview unit tests | 16 passed |
| Desktop/mobile browser suite | 42 passed locally |
| React production build | Passed |

The browser suite covers storm clearing, half/future/shared-location actions, actual colors, placement guides, source highlights and saved geometry. Added responsive checks cover 320x740, 390x844, 430x932, 768x1024 and 844x390 in desktop and mobile Chromium contexts, plus desktop/phone switching, draft preservation, mobile newlines and help-dialog alignment. Desktop behavior and existing editing/undo/error tests remain green.

## Evaluation method

The ninth sample freezes all 50 strings, gold actions, 40 core/10 broader-probe scopes and backend fingerprints before first prediction. Normalized exact-overlap checks include all nine earlier datasets, Python regression literals, browser smoke/responsive/capture and UI example literals, README/archive lines and decoded example links. Similar grammar is intentional; semantic independence is not claimed.

The author saw the implementation and earlier failures. These are implementation-aware hand-authored diagnostics, not independent human-labeled or random real-user accuracy estimates. No parser rules or gold labels were changed after ninth-set predictions. Different fresh samples are not paired before/after measurements.

**Fresh: 40/50 (80%), with 40/40 core and 0/10 broader probes.** Nine core commands expect no actions for invalid/zero/negated inputs; the other 31 expect actual actions. Parser scores do not measure sprite size, placement geometry or cross-request conversation.

| Set | Previous round | Current round |
|---|---:|---:|
| Saved diagnostic set 1 | 50/50 (100.0%) | 50/50 (100.0%) |
| Saved diagnostic set 2 | 48/50 (96.0%) | 48/50 (96.0%) |
| Saved diagnostic set 3 | 45/50 (90.0%) | 45/50 (90.0%) |
| Saved diagnostic set 4 | 46/50 (92.0%) | 46/50 (92.0%) |
| Saved diagnostic set 5 | 47/50 (94.0%) | 47/50 (94.0%) |
| Saved diagnostic set 6 | 45/50 (90.0%) | 46/50 (92.0%) |
| Saved diagnostic set 7 | 44/50 (88.0%) | 45/50 (90.0%) |
| Saved diagnostic set 8 | 40/50 (80.0%) | 44/50 (88.0%) |
| Ninth fresh 50 | First execution | 40/50 (80.0%) |

| Per-command metric | Set 1 | Set 2 | Set 3 | Set 4 | Set 5 | Set 6 | Set 7 | Set 8 | Fresh 9 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Intent sequence | 50/50 (100.0%) | 48/50 (96.0%) | 45/50 (90.0%) | 47/50 (94.0%) | 48/50 (96.0%) | 46/50 (92.0%) | 45/50 (90.0%) | 44/50 (88.0%) | 41/50 (82.0%) |
| Objects/counts/colors | 50/50 (100.0%) | 48/50 (96.0%) | 46/50 (92.0%) | 47/50 (94.0%) | 47/50 (94.0%) | 47/50 (94.0%) | 45/50 (90.0%) | 44/50 (88.0%) | 41/50 (82.0%) |
| Spatial, gold-spatial subset | 22/22 (100.0%) | 18/19 (94.7%) | 18/21 (85.7%) | 12/13 (92.3%) | 7/8 (87.5%) | 9/9 (100.0%) | 7/7 (100.0%) | 4/4 (100.0%) | 12/13 (92.3%) |
| Settings, gold-setting subset | 6/6 (100.0%) | 5/5 (100.0%) | 3/4 (75.0%) | 1/2 (50.0%) | 2/2 (100.0%) | 1/2 (50.0%) | 2/2 (100.0%) | 9/9 (100.0%) | 5/5 (100.0%) |

Exact match compares every field of every ordered action dictionary. Field metrics compare per-command sequences, not tokens. Object metrics include empty typed-action lists; spatial/settings metrics use gold-bearing subsets.

## Main remaining errors

All ten broader ninth-set probes fail; no parser exceptions occurred. P42 and P49 silently emit default-colored objects instead of the requested distribution. The eight saved sets retain 29 errors, fully detailed below.

| Pattern | Case | Actual behavior |
|---|---|---|
| Total inside a part phrase | P41 | `with a total of eight roofs` abstains. |
| Quarter distribution | P42 | Creates eight default-colored trees, without notice. |
| Semicolon remainder | P43 | Ends collection scope and refuses. |
| Latter reference | P44 | Omits the extra group, with notice. |
| Multiplicative groups | P45 | `four bunches of three` abstains. |
| Subordinate creation | P46 | Preservation swallows `while planting`, with notice. |
| Future perfect | P47 | `will have been painted` abstains. |
| Others remainder | P48 | `the others` is unsupported; total mismatch refuses. |
| Each word order | P49 | `three flowers of each color` produces three default-colored flowers, without notice. |
| Mixed-type shared location | P50 | Creates both types but drops placement, with notice. |

Prioritize silent incorrect execution (P42/P49), then modifier scope across object types and collection references. Do not interpret notices as proof that unsupported requests caused no scene changes; partial actions are shown below.

## All 50 fresh commands

| ID | Scope | Result | Command |
|---|---|---|---|
| P01 | core | PASS | End the storm. |
| P02 | core | PASS | Stop the shower. |
| P03 | core | PASS | Make it dawn and stop the rain. |
| P04 | core | PASS | Never end the storm; plant two pink flowers. |
| P05 | core | PASS | Make it snow and end the snow. |
| P06 | core | PASS | Stop storm; place a purple flower. |
| P07 | core | PASS | Build twelve houses: half orange and half pink. |
| P08 | core | PASS | Create fourteen flowers, half white and half purple. |
| P09 | core | PASS | Plant ten trees: half of them blue and half of them purple. |
| P10 | core | PASS | Draw flowers, a total of six: half orange and half red. |
| P11 | core | PASS | Build four green houses: half small ones and half big ones. |
| P12 | core | PASS | Build two cottages: half blue and half pink; put a rock between them. |
| P13 | core | PASS | Plant six trees: half orange and the rest white; remove them. |
| P14 | core | PASS | Add eight flowers: half yellow and half purple near the pond. |
| P15 | core | PASS | Build nine houses: half blue and half orange. |
| P16 | core | PASS | Plant trees: half red and half white. |
| P17 | core | PASS | Create six flowers: half pink, half blue, and half yellow. |
| P18 | core | PASS | Place zero flowers: half red and half yellow. |
| P19 | core | PASS | Build four homes: one blue and three white, all right of the lake. |
| P20 | core | PASS | Plant trees: two each of pink and green, all behind the house. |
| P21 | core | PASS | Place flowers: one white and two yellow, all near the bridge. |
| P22 | core | PASS | Build six houses: two orange and four green, all between the lake and the tower. |
| P23 | core | PASS | Build two cottages, one pink and one orange, all across the river. |
| P24 | core | PASS | Plant four trees: one blue and the rest green, all near the castle. |
| P25 | core | PASS | Create six flowers: half pink and half blue, all below the tower. |
| P26 | core | PASS | Plant trees: two whose leaves are white and three whose leaves are purple, all left of the mountain. |
| P27 | core | PASS | Build four houses: half pink and half white, all near. |
| P28 | core | PASS | Create trees: two yellow and three green, all not near the castle. |
| P29 | core | PASS | Place a house whose roof shall be painted yellow. |
| P30 | core | PASS | Plant a tree whose leaves will be coloured pink. |
| P31 | core | PASS | Create flowers whose petals will be freshly coloured purple. |
| P32 | core | PASS | Build two houses with roofs which will be painted green. |
| P33 | core | PASS | Behind the lake, place a cottage whose roof will be colored blue. |
| P34 | core | PASS | Create a home with a roof that shall be painted orange. |
| P35 | core | PASS | Build six houses: half whose roofs will be painted white and half whose roofs will be painted blue, all beside the pond. |
| P36 | core | PASS | Build four cottages: one whose roof will be painted pink and the rest whose roofs will be painted orange. |
| P37 | core | PASS | Add two houses whose roofs shall be painted white; remove them. |
| P38 | core | PASS | Create a house whose roof will not be coloured purple. |
| P39 | core | PASS | Place a boulder whose leaves will be painted green. |
| P40 | core | PASS | Build a house whose roof will be painted yellow or purple. |
| P41 | capability_probe | FAIL | Build houses with a total of eight roofs painted white. |
| P42 | capability_probe | FAIL | Plant eight trees: one quarter blue and three quarters white. |
| P43 | capability_probe | FAIL | Create six cottages: two green; the rest purple. |
| P44 | capability_probe | FAIL | Add flowers, one yellow and two pink; create two more of the latter. |
| P45 | capability_probe | FAIL | Draw four bunches of three purple flowers. |
| P46 | capability_probe | FAIL | Keep the tower intact while planting four green trees. |
| P47 | capability_probe | FAIL | Build a cottage whose roof will have been painted white. |
| P48 | capability_probe | FAIL | Plant six trees: two blue and the others purple. |
| P49 | capability_probe | FAIL | Add three flowers of each color: red and white. |
| P50 | capability_probe | FAIL | Build two blue houses and three yellow flowers, all beside the lake. |

## Ninth-set failures

### P41: Build houses with a total of eight roofs painted white.

Expected:

```json
[
  {
    "action": "add",
    "type": "house",
    "count": 8,
    "color": "white"
  }
]
```

Actual:

```json
[]
```

Notices: Unsupported, negated or ambiguous post-noun color; that object instruction was skipped.

### P42: Plant eight trees: one quarter blue and three quarters white.

Expected:

```json
[
  {
    "action": "add",
    "type": "tree",
    "count": 2,
    "color": "blue"
  },
  {
    "action": "add",
    "type": "tree",
    "count": 6,
    "color": "white"
  }
]
```

Actual:

```json
[
  {
    "action": "add",
    "type": "tree",
    "count": 8,
    "color": null
  }
]
```

Notices: None.

### P43: Create six cottages: two green; the rest purple.

Expected:

```json
[
  {
    "action": "add",
    "type": "house",
    "count": 2,
    "color": "green"
  },
  {
    "action": "add",
    "type": "house",
    "count": 4,
    "color": "purple"
  }
]
```

Actual:

```json
[]
```

Notices: Partition counts do not match the declared total; that object instruction was skipped.; No supported object or setting found in one clause. Name an object explicitly; pronoun references are not resolved.

### P44: Add flowers, one yellow and two pink; create two more of the latter.

Expected:

```json
[
  {
    "action": "add",
    "type": "flower",
    "count": 1,
    "color": "yellow"
  },
  {
    "action": "add",
    "type": "flower",
    "count": 2,
    "color": "pink"
  },
  {
    "action": "add",
    "type": "flower",
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
    "type": "flower",
    "count": 1,
    "color": "yellow"
  },
  {
    "action": "add",
    "type": "flower",
    "count": 2,
    "color": "pink"
  }
]
```

Notices: No supported object or setting found in one clause. Name an object explicitly; pronoun references are not resolved.

### P45: Draw four bunches of three purple flowers.

Expected:

```json
[
  {
    "action": "add",
    "type": "flower",
    "count": 12,
    "color": "purple"
  }
]
```

Actual:

```json
[]
```

Notices: Skipped flower: specify an unambiguous non-negative whole-number quantity.

### P46: Keep the tower intact while planting four green trees.

Expected:

```json
[
  {
    "action": "add",
    "type": "tree",
    "count": 4,
    "color": "green"
  }
]
```

Actual:

```json
[]
```

Notices: Preserved referenced objects; no creation or removal was applied for that clause.

### P47: Build a cottage whose roof will have been painted white.

Expected:

```json
[
  {
    "action": "add",
    "type": "house",
    "count": 1,
    "color": "white"
  }
]
```

Actual:

```json
[]
```

Notices: Unsupported, negated or ambiguous post-noun color; that object instruction was skipped.

### P48: Plant six trees: two blue and the others purple.

Expected:

```json
[
  {
    "action": "add",
    "type": "tree",
    "count": 2,
    "color": "blue"
  },
  {
    "action": "add",
    "type": "tree",
    "count": 4,
    "color": "purple"
  }
]
```

Actual:

```json
[]
```

Notices: Partition counts do not match the declared total; that object instruction was skipped.

### P49: Add three flowers of each color: red and white.

Expected:

```json
[
  {
    "action": "add",
    "type": "flower",
    "count": 3,
    "color": "red"
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
    "count": 3,
    "color": null
  }
]
```

Notices: None.

### P50: Build two blue houses and three yellow flowers, all beside the lake.

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
    "type": "flower",
    "count": 3,
    "color": "yellow",
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
    "type": "flower",
    "count": 3,
    "color": "yellow"
  }
]
```

Notices: Skipped a context-only or unsupported instruction; use an explicit add/build/plant verb to create objects.


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


## Saved set 8 failures

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

## Reproduce

Use new output names for future retests to preserve historical evidence. From the root:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests
.\.venv\Scripts\python.exe -m tests.evaluate
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/heldout_commands.json --dataset-sha256 d372d2d85208319439929068902779ba4ea9144722caea783a8c792bcbd7a224 --allow-parser-change --output evaluation/heldout_retest_v9.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v2.json --dataset-sha256 050f1f92dba55b89883ebd05c4dc074b287c230a65f33f3d12a7a321ee17042b --allow-parser-change --output evaluation/fresh_v2_retest_v9.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v3.json --dataset-sha256 bc902a965baba135a0b81dc0774230921ed49a82bb510305a771da0e1a684927 --allow-parser-change --output evaluation/fresh_v3_retest_v9.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v4.json --dataset-sha256 83f280f866430ebcabf50de1ac3741a62da42d74757f20fb97db2c675c62a0cd --allow-parser-change --output evaluation/fresh_v4_retest_v9.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v5.json --dataset-sha256 e20bbe0ba47f12431c33708b4aa653ce8689a2b9027aca7294747dc0c0f9bc8e --allow-parser-change --output evaluation/fresh_v5_retest_v9.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v6.json --dataset-sha256 b4c823eafa84322f3c164fcaa0080bf5ed4f94f61d374c8dcd2145c74fed3703 --allow-parser-change --output evaluation/fresh_v6_retest_v9.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v7.json --dataset-sha256 b1c66ed63c5747d59c87b9baaf37f923307cf9d1d42868e7bfeb1ef3fef4b85e --allow-parser-change --output evaluation/fresh_v7_retest_v9.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v8.json --dataset-sha256 44e7288480226cbe1597aa5d925fd41b518b43bec82b260104ffe266c4be1dc5 --allow-parser-change --output evaluation/fresh_v8_retest_v9.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v9.json --dataset-sha256 393d87061735968e5d33452530c341e1ff8ffbe9aa88418932d6f4440b44d475 --output evaluation/fresh_results_v9.json
.\.venv\Scripts\python.exe -X utf8 -m evaluation.write_shared_report
```

From `frontend/`: `npm test`, `npm run build`, `npm run test:e2e` with both servers running. Set `WORDWORLD_BASE_URL` to test production.

Gold: `tests/fresh_commands_v9.json`. Predictions/notices: `evaluation/fresh_results_v9.json`. Regressions: `tests/test_shared_fixes.py`, `frontend/tests/browser/mobile.spec.js`, `frontend/tests/browser/smoke.spec.js`.

Parser SHA256: `7261486fe45b390f216d5e74cbbb98c31cc79dbb3a8698ee4c002a5e9401fbdf`.
Backend pipeline SHA256: `7480829f7f7b7372c5b94e3a8ae72fe83594d7e0c12b412fc3a79aa6a7d77f0f`.
Ninth dataset SHA256: `393d87061735968e5d33452530c341e1ff8ffbe9aa88418932d6f4440b44d475`.

All nine evaluations verified the same backend fingerprint before and after prediction. No subsequent backend or gold tuning occurred.
