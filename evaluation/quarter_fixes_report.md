# WordWorld quarter, of-each-color, mixed-location and future-perfect fixes — 15 October 2026

**Nine saved-set retests: 50/50 (100.0%), 48/50 (96.0%), 45/50 (90.0%), 46/50 (92.0%), 47/50 (94.0%), 46/50 (92.0%), 45/50 (90.0%), 44/50 (88.0%), 44/50 (88.0%). Tenth fresh set: 40/50 (80.0%).**

All four targeted ninth-set errors pass: P42 (quarters), P49 (of each color), P50 (mixed shared placement) and P47 (future perfect). The ninth set improves from 40/50 to 44/50. No previously passing exact match regressed across the nine saved sets. Historical labels and first-run predictions are unchanged.

## Changes

- Quarter groups reuse fraction partitions with explicit numerator/denominator arithmetic. Supports a/one/two/three quarters, digits, hyphenated forms, of them, mapped part colors, mixed halves/quarters and inferred rest. A declared total must yield whole non-negative object counts, and group sums must agree with it. Missing totals, nonintegral groups, invalid numerators and inconsistent partitions abstain. Arithmetic precedes the existing 16-per-action cap.
- Adjacent `of each color/colour` lists expand one explicit noun count across distinct supported colors. Lists can use a colon or comma and remain scoped to that noun. Missing/invalid counts, unsupported/duplicate colors and contradictory source colors abstain. Counts, spans, references, limits and mixed follow-on nouns use the existing action schema.
- Shared `, all <location>` tails resolve once before source objects enter request-local reference state. Every source group in the same creation clause receives that placement, including mixed types and quarter/each groups. A new explicit verb begins another clause. Missing/chained/negated/conflicting locations and spatially filtered removal abstain. Pronoun landmark bindings continue pointing to the prior introductions.
- Mapped roof/foliage/petal clauses accept will/shall have been painted/colored/coloured with bounded passive adverbs. Negation and unmapped parts abstain. Whole-object future-perfect clauses without an explicit mapped part remain unsupported.
- Fixed a reporting-only evaluator error: empty spatial/settings subsets display N/A instead of formatting None as a percentage. The tenth sample has zero settings cases. Its original CLI printed the main scores and failed after saving all first-run predictions; a retry to a separate ignored output matched that preserved JSON exactly. No backend or gold changes followed the fresh run.

## Verification

| Check | Result |
|---|---|
| Python parser/API/evaluator suite | 525 passed; 58 grammar cases and one evaluator regression added |
| Original development commands | 50/50 exact actions |
| Scene/preview unit tests | 16 passed |
| Desktop/mobile browser suite | 44 passed locally |
| React production build | Passed |

The added browser flow verifies visible blue/white quarter foliage, red/white each-color groups, common anchor IDs for mixed houses/flowers near the lake, a purple future-perfect roof, source highlights and undo/redo. Existing five-width mobile/tablet/landscape checks remain green. Screenshots: `.runtime/quarter-fixes-desktop.png` and `.runtime/quarter-fixes-mobile.png`.

## Evaluation method

The tenth sample freezes all 50 strings, expected action dictionaries, 40 core/10 broader-probe scopes and backend fingerprints before first prediction. Normalized exact-overlap checks include all ten earlier datasets, Python test literals, browser smoke/responsive/capture and UI example literals, README/archive lines and decoded example links. Similar grammar is intentional; semantic independence is not claimed.

The author saw the implementation and earlier errors. These are implementation-aware hand-authored diagnostics, not independent human-labeled or random real-user accuracy estimates. No parser rules or gold labels were tuned after tenth-set predictions. The evaluator console-only fix did not change predictions or backend fingerprints. Different fresh samples are not paired before/after measurements.

**Fresh: 40/50 (80%), with 40/40 core and 0/10 broader probes.** Eleven core commands expect no actions for zero/invalid/negated forms; 29 expect actual actions. No settings-bearing commands were included, so fresh settings accuracy is N/A, not 0%. Geometry and cross-request conversations are not scored.

| Set | Previous round | Current round |
|---|---:|---:|
| Saved diagnostic set 1 | 50/50 (100.0%) | 50/50 (100.0%) |
| Saved diagnostic set 2 | 48/50 (96.0%) | 48/50 (96.0%) |
| Saved diagnostic set 3 | 45/50 (90.0%) | 45/50 (90.0%) |
| Saved diagnostic set 4 | 46/50 (92.0%) | 46/50 (92.0%) |
| Saved diagnostic set 5 | 47/50 (94.0%) | 47/50 (94.0%) |
| Saved diagnostic set 6 | 46/50 (92.0%) | 46/50 (92.0%) |
| Saved diagnostic set 7 | 45/50 (90.0%) | 45/50 (90.0%) |
| Saved diagnostic set 8 | 44/50 (88.0%) | 44/50 (88.0%) |
| Saved diagnostic set 9 | 40/50 (80.0%) | 44/50 (88.0%) |
| Tenth fresh 50 | First execution | 40/50 (80.0%) |

| Per-command metric | Set 1 | Set 2 | Set 3 | Set 4 | Set 5 | Set 6 | Set 7 | Set 8 | Set 9 | Fresh 10 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Intent sequence | 50/50 (100.0%) | 48/50 (96.0%) | 45/50 (90.0%) | 47/50 (94.0%) | 48/50 (96.0%) | 46/50 (92.0%) | 45/50 (90.0%) | 44/50 (88.0%) | 44/50 (88.0%) | 40/50 (80.0%) |
| Objects/counts/colors | 50/50 (100.0%) | 48/50 (96.0%) | 46/50 (92.0%) | 47/50 (94.0%) | 47/50 (94.0%) | 47/50 (94.0%) | 45/50 (90.0%) | 44/50 (88.0%) | 44/50 (88.0%) | 40/50 (80.0%) |
| Spatial, gold-spatial subset | 22/22 (100.0%) | 18/19 (94.7%) | 18/21 (85.7%) | 12/13 (92.3%) | 7/8 (87.5%) | 9/9 (100.0%) | 7/7 (100.0%) | 4/4 (100.0%) | 13/13 (100.0%) | 11/11 (100.0%) |
| Settings, gold-setting subset | 6/6 (100.0%) | 5/5 (100.0%) | 3/4 (75.0%) | 1/2 (50.0%) | 2/2 (100.0%) | 1/2 (50.0%) | 2/2 (100.0%) | 9/9 (100.0%) | 5/5 (100.0%) | 0/0 (N/A) |

Exact match compares every field of every ordered action dictionary. Field metrics compare per-command sequences, not tokens. Object metrics include empty typed-action lists; spatial/settings metrics use gold-bearing subsets.

## Main remaining errors

All ten broader tenth-set probes fail; no parser exceptions occurred. Q42, Q47 and Q49 silently create default-colored objects instead of the requested distribution. The nine saved sets retain 35 errors, fully detailed below.

| Pattern | Case | Actual behavior |
|---|---|---|
| Total inside part phrase | Q41 | `with a total of seven roofs` abstains. |
| Thirds | Q42 | Adds twelve default-colored trees, without notice. |
| Semicolon remainder | Q43 | Ends partition scope and refuses. |
| Former reference | Q44 | Omits the additional group, with notice. |
| Multiplicative groups | Q45 | `three clusters of four` abstains. |
| Subordinate creation | Q46 | Preservation swallows `while building`, with notice. |
| Percentage distribution | Q47 | Adds eight default-colored flowers, without notice. |
| Trailing each count | Q48 | `three of each` after the color list abstains. |
| Alternate each word order | Q49 | `in each of blue and green` produces two default-color houses, without notice. |
| Whole-object future perfect | Q50 | `a cottage that will have been painted blue` abstains without an explicit roof. |

Prioritize silent incorrect distribution (thirds, percentages and alternate each wording), then collection references and scope across clauses. Full predictions distinguish refusal, partial execution and incorrect actions.

## All 50 fresh commands

| ID | Scope | Result | Command |
|---|---|---|---|
| Q01 | core | PASS | Create twelve flowers: one quarter pink and three quarters orange. |
| Q02 | core | PASS | Plant eight trees: two quarters green and half white. |
| Q03 | core | PASS | Build sixteen homes: one quarter with orange roofs and the rest with purple roofs. |
| Q04 | core | PASS | Place twenty flowers: a quarter blue and three quarters yellow. |
| Q05 | core | PASS | Plant four trees: one quarter of them blue and three quarters of them red. |
| Q06 | core | PASS | Create eight flowers: quarter purple, quarter pink, and half white. |
| Q07 | core | PASS | Build houses, a total of twelve: one quarter blue and the remainder green. |
| Q08 | core | PASS | Behind the lake, plant eight trees: a quarter orange and three-quarters white. |
| Q09 | core | PASS | Create zero flowers: one quarter white and three quarters pink. |
| Q10 | core | PASS | Build ten houses: one quarter purple and three quarters yellow. |
| Q11 | core | PASS | Plant sixteen trees: three quarters blue and half pink. |
| Q12 | core | PASS | Place flowers: one quarter pink and three quarters purple. |
| Q13 | core | PASS | Add a flower of each color: purple, white and pink. |
| Q14 | core | PASS | Plant four trees of each colour: yellow and green. |
| Q15 | core | PASS | Build exactly two homes of each color: orange, blue, and white. |
| Q16 | core | PASS | Draw three flowers of each colour, pink and purple. |
| Q17 | core | PASS | Place a pair of houses of each color: white and green near the pond. |
| Q18 | core | PASS | Plant half a dozen trees of each color: pink and white. |
| Q19 | core | PASS | Create one flower of each color: red and white; remove them. |
| Q20 | core | PASS | Add two flowers of each color: blue and gray. |
| Q21 | core | PASS | Plant two green trees of each color: red and purple. |
| Q22 | core | PASS | Add two flowers of each color: pink and purple and a house, all near the bridge. |
| Q23 | core | PASS | Place a flower and a tower, all behind the castle. |
| Q24 | core | PASS | Build two houses and plant three trees, all below the tower. |
| Q25 | core | PASS | Place two flowers and a rock, all between the house and the castle. |
| Q26 | core | PASS | Draw a mountain and two white flowers, all right of the lake. |
| Q27 | core | PASS | Build one home; plant two trees and a flower, all near it. |
| Q28 | core | PASS | Build two cottages; add a flower and a tower, all between them. |
| Q29 | core | PASS | Build eight houses: one quarter blue and three quarters white and three purple flowers, all near the road. |
| Q30 | core | PASS | Place a tower and two trees, all not near the river. |
| Q31 | core | PASS | Build a house beside the lake and two flowers, all left of the tower. |
| Q32 | core | PASS | Draw a rock and a mountain, all near. |
| Q33 | core | PASS | Build two houses whose roofs will already have been painted orange. |
| Q34 | core | PASS | Plant a tree whose foliage will have just been coloured red. |
| Q35 | core | PASS | Create flowers whose petals will have been freshly coloured yellow. |
| Q36 | core | PASS | Build a house with a roof that shall have been painted white behind the river. |
| Q37 | core | PASS | Build four houses: one quarter whose roofs will have been painted pink and three quarters whose roofs will have been painted blue. |
| Q38 | core | PASS | Build two houses whose roofs will have been coloured purple; remove them. |
| Q39 | core | PASS | Build a cottage whose roof will not have been painted orange. |
| Q40 | core | PASS | Create a castle whose petals will have been painted red. |
| Q41 | capability_probe | FAIL | Build cottages with a total of seven roofs painted red. |
| Q42 | capability_probe | FAIL | Plant twelve trees: one third purple and two thirds green. |
| Q43 | capability_probe | FAIL | Build eight houses: two blue; the rest yellow. |
| Q44 | capability_probe | FAIL | Add flowers, two white and three pink; create one more of the former. |
| Q45 | capability_probe | FAIL | Draw three clusters of four orange flowers. |
| Q46 | capability_probe | FAIL | Preserve the castle while building three white cottages. |
| Q47 | capability_probe | FAIL | Create eight flowers: 25% pink and 75% purple. |
| Q48 | capability_probe | FAIL | Add flowers in red and blue, three of each. |
| Q49 | capability_probe | FAIL | Build one pair of cottages in each of blue and green. |
| Q50 | capability_probe | FAIL | Build a cottage that will have been painted blue. |

## Tenth-set failures

### Q41: Build cottages with a total of seven roofs painted red.

Expected:

```json
[
  {
    "action": "add",
    "type": "house",
    "count": 7,
    "color": "red"
  }
]
```

Actual:

```json
[]
```

Notices: Unsupported, negated or ambiguous post-noun color; that object instruction was skipped.

### Q42: Plant twelve trees: one third purple and two thirds green.

Expected:

```json
[
  {
    "action": "add",
    "type": "tree",
    "count": 4,
    "color": "purple"
  },
  {
    "action": "add",
    "type": "tree",
    "count": 8,
    "color": "green"
  }
]
```

Actual:

```json
[
  {
    "action": "add",
    "type": "tree",
    "count": 12,
    "color": null
  }
]
```

Notices: None.

### Q43: Build eight houses: two blue; the rest yellow.

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
    "count": 6,
    "color": "yellow"
  }
]
```

Actual:

```json
[]
```

Notices: Partition counts do not match the declared total; that object instruction was skipped.; No supported object or setting found in one clause. Name an object explicitly; pronoun references are not resolved.

### Q44: Add flowers, two white and three pink; create one more of the former.

Expected:

```json
[
  {
    "action": "add",
    "type": "flower",
    "count": 2,
    "color": "white"
  },
  {
    "action": "add",
    "type": "flower",
    "count": 3,
    "color": "pink"
  },
  {
    "action": "add",
    "type": "flower",
    "count": 1,
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
    "count": 2,
    "color": "white"
  },
  {
    "action": "add",
    "type": "flower",
    "count": 3,
    "color": "pink"
  }
]
```

Notices: No supported object or setting found in one clause. Name an object explicitly; pronoun references are not resolved.

### Q45: Draw three clusters of four orange flowers.

Expected:

```json
[
  {
    "action": "add",
    "type": "flower",
    "count": 12,
    "color": "orange"
  }
]
```

Actual:

```json
[]
```

Notices: Skipped flower: specify an unambiguous non-negative whole-number quantity.

### Q46: Preserve the castle while building three white cottages.

Expected:

```json
[
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

Notices: Preserved referenced objects; no creation or removal was applied for that clause.

### Q47: Create eight flowers: 25% pink and 75% purple.

Expected:

```json
[
  {
    "action": "add",
    "type": "flower",
    "count": 2,
    "color": "pink"
  },
  {
    "action": "add",
    "type": "flower",
    "count": 6,
    "color": "purple"
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

### Q48: Add flowers in red and blue, three of each.

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
    "color": "blue"
  }
]
```

Actual:

```json
[]
```

Notices: An inherited noun group needs an explicit quantity; that object instruction was skipped.; No supported object or setting found in one clause. Name an object explicitly; pronoun references are not resolved.

### Q49: Build one pair of cottages in each of blue and green.

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
[
  {
    "action": "add",
    "type": "house",
    "count": 2,
    "color": null
  }
]
```

Notices: None.

### Q50: Build a cottage that will have been painted blue.

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


## Saved set 9 failures

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

## Reproduce

Use new output names for future retests to preserve historical evidence. From the root:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests
.\.venv\Scripts\python.exe -m tests.evaluate
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/heldout_commands.json --dataset-sha256 d372d2d85208319439929068902779ba4ea9144722caea783a8c792bcbd7a224 --allow-parser-change --output evaluation/heldout_retest_v10.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v2.json --dataset-sha256 050f1f92dba55b89883ebd05c4dc074b287c230a65f33f3d12a7a321ee17042b --allow-parser-change --output evaluation/fresh_v2_retest_v10.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v3.json --dataset-sha256 bc902a965baba135a0b81dc0774230921ed49a82bb510305a771da0e1a684927 --allow-parser-change --output evaluation/fresh_v3_retest_v10.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v4.json --dataset-sha256 83f280f866430ebcabf50de1ac3741a62da42d74757f20fb97db2c675c62a0cd --allow-parser-change --output evaluation/fresh_v4_retest_v10.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v5.json --dataset-sha256 e20bbe0ba47f12431c33708b4aa653ce8689a2b9027aca7294747dc0c0f9bc8e --allow-parser-change --output evaluation/fresh_v5_retest_v10.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v6.json --dataset-sha256 b4c823eafa84322f3c164fcaa0080bf5ed4f94f61d374c8dcd2145c74fed3703 --allow-parser-change --output evaluation/fresh_v6_retest_v10.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v7.json --dataset-sha256 b1c66ed63c5747d59c87b9baaf37f923307cf9d1d42868e7bfeb1ef3fef4b85e --allow-parser-change --output evaluation/fresh_v7_retest_v10.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v8.json --dataset-sha256 44e7288480226cbe1597aa5d925fd41b518b43bec82b260104ffe266c4be1dc5 --allow-parser-change --output evaluation/fresh_v8_retest_v10.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v9.json --dataset-sha256 393d87061735968e5d33452530c341e1ff8ffbe9aa88418932d6f4440b44d475 --allow-parser-change --output evaluation/fresh_v9_retest_v10.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v10.json --dataset-sha256 9ef33daf26d8e90aaf06df666a76d04d6b2fdcf777e4b805e741ba57b019c79a --output evaluation/fresh_results_v10.json
.\.venv\Scripts\python.exe -X utf8 -m evaluation.write_quarter_report
```

From `frontend/`: `npm test`, `npm run build`, `npm run test:e2e` with both servers running. Set `WORDWORLD_BASE_URL` for production checks.

Gold: `tests/fresh_commands_v10.json`. First predictions: `evaluation/fresh_results_v10.json`. Regressions: `tests/test_quarter_fixes.py`, `tests/test_evaluation_empty_metrics.py`, `frontend/tests/browser/smoke.spec.js`.

Parser SHA256: `4a6cf43957656cb7a5d814c44046f260e1fbaeba0f3d1b8dcd4f451d4a1bd37a`.
Backend pipeline SHA256: `ccca65ca61f9189dbb03aebc51d34d7c76fa859a2259f1dc41e5e7d2b6fd345b`.
Tenth dataset SHA256: `9ef33daf26d8e90aaf06df666a76d04d6b2fdcf777e4b805e741ba57b019c79a`.

All ten evaluations verified the same backend fingerprint before and after prediction. Original labels/results were preserved.
