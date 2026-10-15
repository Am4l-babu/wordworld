# WordWorld post-noun and coordination fixes — 15 October 2026

**Three saved-set retests: 50/50 (100.0%), 47/50 (94.0%), 45/50 (90.0%). Fourth fresh set: 40/50 (80.0%).**

All five previously observed target errors now pass: F46 (blue roof), G41 (orange roof), G42 (whose roof is green), G49 (houses, three of them), and G50 (two small and three large houses). Historical labels and results were preserved.

The fourth sample was hand-authored and frozen before its first parser execution, including expected actions, scopes, and backend source hashes. There are no normalized exact overlaps with the four earlier datasets (the development 50 and three diagnostic sets), Python regression string literals, browser smoke-test literals or README lines at freeze time. Similar grammar is intentional. The author saw the implementation and earlier failures; this is a diagnostic sample, not an independent human-labeled benchmark or random real-user accuracy estimate.

## Changes and scope

- Adjacent post-noun colors attach to the source object: `with a blue roof`, `whose roof is green`, `that/which is pink`, and corresponding tree leaves/foliage and flower petals. These use existing visible color fields. Shared post-noun colors apply to separately counted coordinated groups.
- Appositive quantities such as `houses, three of them`, `trees, five in total`, and `half a dozen altogether` are read before creation. The appositive `them` is consumed as part of the quantity, not as an extra action/reference. Final counts feed reference resolution and obey the existing 16-per-action cap.
- Shared-noun coordination no longer needs colors: `two small and three large houses` becomes two add actions, with counts two and three. Comma lists, mixed colored/uncolored groups, shared placement, and per-group negation work. Each group needs an explicit count or article. Numeric conjunctions such as `one hundred and two` remain intact.
- Contradictory prefix/post-noun counts or colors, ambiguous counts, negative/fractional quantities, missing group quantities, and unsupported color/part mappings abstain with notices. Zero groups add nothing. Repeated identical colors/counts are allowed.
- Post-noun attributes stop at other subjects and placement phrases. Landmark attributes cannot bleed into following source objects; they do not select landmarks by color. The API and action schema stay compatible with the existing frontend. spaCy supplies annotations; action grounding remains rule based.

**Limits:** Small/large are group descriptors only; size rendering is not implemented or scored. This is bounded grammar, not general post-noun English: the new sample still fails `painted blue`, nested roof clauses, `exactly five`, `five in all`, `ones`, group multiplication and relative-clause coordination. No backend or gold-label changes were made after observing the fourth-set predictions.

## Verification

| Check | Result |
|---|---|
| Python parser/API tests | 223 passed; 53 new regression cases |
| Original development 50 | 50/50 exact matches |
| Scene/preview unit tests | 16 passed |
| Desktop/mobile Chromium integration | 18 passed |
| React production build | Passed |
| Local servers | FastAPI health OK with spaCy; Vite HTTP 200 |

The new browser flow verifies three new blue roofs, five new purple-foliage trees from two count groups, exact inline quantity/color spans, and creation followed by reference removal preserving older houses. Undo/redo and existing object manipulations also pass. Both desktop and mobile screenshots were inspected: `.runtime/postnoun-fixes-desktop.png` and `.runtime/postnoun-fixes-mobile.png`.

## Results

| Set | Previous round | Current round | Interpretation |
|---|---:|---:|---|
| Diagnostic set 1 | 50/50 (100.0%) | 50/50 (100.0%) | Same frozen labels; development retest |
| Diagnostic set 2 | 46/50 (92.0%) | 47/50 (94.0%) | Same frozen labels; development retest |
| Diagnostic set 3 | 41/50 (82.0%) | 45/50 (90.0%) | Same frozen labels; development retest |
| Fourth fresh 50 | Not run previously | 40/50 (80.0%) | First predictions after label/code freeze |

| Metric | Set 1 retest | Set 2 retest | Set 3 retest | New set 4 |
|---|---:|---:|---:|---:|
| Intent sequence | 50/50 (100.0%) | 47/50 (94.0%) | 45/50 (90.0%) | 43/50 (86.0%) |
| Objects/counts/colors | 50/50 (100.0%) | 48/50 (96.0%) | 46/50 (92.0%) | 41/50 (82.0%) |
| Spatial fields on gold-spatial commands | 22/22 (100.0%) | 18/19 (94.7%) | 18/21 (85.7%) | 12/13 (92.3%) |
| Settings on gold-setting commands | 6/6 (100.0%) | 4/5 (80.0%) | 3/4 (75.0%) | 1/2 (50.0%) |

The fresh set has **40/40 core matches and 0/10 broader probes**. Core includes two zero/negative-count refusal cases, one deliberately informal phrase within the implemented grammar, and one named-type landmark case that does not test color filtering. Its overall 80% must be reported together with this split. Different sets have different distributions; the fresh score is not a paired before/after comparison.

Exact match requires every field of every ordered action dictionary. Field metrics are per-command sequence comparisons, not token scores. The object metric includes matching empty typed-action lists for pure settings. Spatial and setting denominators are their gold-bearing subsets. Parser scores do not validate scene geometry or cross-request context.

## Remaining NLP errors

The fourth sample has 10 errors and no exceptions. Four failures (H44–H46 and H50) emit partial actions without any notice; these need explicit detection as well as expanded grammar.

| Priority / pattern | Cases | Observed problem |
|---|---|---|
| Quantity modifiers and tails | H42, H45, H47 | `exactly five`, `two groups of three`, and `five in all` create one object instead of five/six. |
| Ellipsis and coordinated relative clauses | H44, H46 | `three large ones` and `and three that are yellow` lose the entire second group without a notice. |
| More varied part-color clauses | H41, H43 | `roofs painted blue` and `a roof that is yellow` abstain with notices. |
| Direction paraphrases | H48 | `northern side of the pond` abstains rather than placing above the lake. |
| Subordinate creation | H49 | Preservation swallows `while planting three trees`; no trees are added. |
| Weather synonyms | H50 | `no precipitation` fails to clear weather; only day is applied, without notice. |

The earlier sets retain eight errors: F35 (daylight), F48 (while adding), F50 (construct); G43 (that crosses), G44 (construct), G45 (while building), G46 (without any rain), G47 (east side of). No new exact-match regressions appeared on the three saved samples.

## All 50 fresh commands

| ID | Scope | Result | Command |
|---|---|---|---|
| H01 | core | PASS | Build four cottages whose roofs are purple. |
| H02 | core | PASS | Plant two trees with yellow foliage. |
| H03 | core | PASS | Create five flowers whose petals are white. |
| H04 | core | PASS | Place a cottage which is pink next to the stream. |
| H05 | core | PASS | Grow three trees having orange leaves. |
| H06 | core | PASS | Add two blossoms in yellow. |
| H07 | core | PASS | Build a cabin with the roof is red. |
| H08 | core | PASS | Place three flowers that are blue behind the tower. |
| H09 | core | PASS | Build cottages, four of them. |
| H10 | core | PASS | Place rocks, a pair of them. |
| H11 | core | PASS | Plant trees, seven altogether. |
| H12 | core | PASS | Add flowers, eleven in total. |
| H13 | core | PASS | Build bridges, two pairs of them across the river. |
| H14 | core | PASS | Place towers, half a dozen in total. |
| H15 | core | PASS | Add stones, thirty-two of them. |
| H16 | core | PASS | Create castles, three of them behind the pond. |
| H17 | core | PASS | Build houses, zero in total; plant two pink flowers. |
| H18 | core | PASS | Add roads, -2 in total; create a tower. |
| H19 | core | PASS | Place two tiny and five large cottages. |
| H20 | core | PASS | Plant a pair of little and four big trees. |
| H21 | core | PASS | Create three small, two large, and a tiny tower. |
| H22 | core | PASS | Draw a small and a large bridge across the creek. |
| H23 | core | PASS | Place two small and four pink flowers. |
| H24 | core | PASS | Build three red and two large homes. |
| H25 | core | PASS | Add two small, one white, and three large trees. |
| H26 | core | PASS | Put a little and two large rocks near the bridge. |
| H27 | core | PASS | Build two small and not four large homes. |
| H28 | core | PASS | Plant zero small and two large trees with purple foliage. |
| H29 | core | PASS | Add cottages, three of them, whose roofs are white; remove two of them. |
| H30 | core | PASS | Build a cottage which is orange; place two flowers near it. |
| H31 | core | PASS | Place flowers with red petals, a pair of them beside the tower. |
| H32 | core | PASS | Behind the castle, plant trees, a dozen of them, with green leaves. |
| H33 | core | PASS | Build one tiny and one large cabin; add a road between them. |
| H34 | core | PASS | Create two little and three large houses whose roofs are orange. |
| H35 | core | PASS | Place flowers that are purple and two cottages with green roofs. |
| H36 | core | PASS | Plant a tree near the cottage with orange roofs and two white flowers. |
| H37 | core | PASS | Keep the lake; build cottages, two of them, with yellow roofs. |
| H38 | core | PASS | Create trees, four of them, with blue leaves; make it night; remove them. |
| H39 | core | PASS | Build houses with pink roofs, a pair of them; remove one of them; remove it. |
| H40 | core | PASS | Add a cottage whose roof is purple; build a bridge spanning the creek. |
| H41 | capability_probe | FAIL | Add three houses with roofs painted blue. |
| H42 | capability_probe | FAIL | Plant flowers, exactly five of them. |
| H43 | capability_probe | FAIL | Build a house with a roof that is yellow. |
| H44 | capability_probe | FAIL | Place two small houses and three large ones. |
| H45 | capability_probe | FAIL | Build houses in two groups of three. |
| H46 | capability_probe | FAIL | Plant two trees that are green and three that are yellow. |
| H47 | capability_probe | FAIL | Add flowers, five in all. |
| H48 | capability_probe | FAIL | Build a house to the northern side of the pond. |
| H49 | capability_probe | FAIL | Preserve the cottage while planting three trees. |
| H50 | capability_probe | FAIL | Make it sunny with no precipitation. |

## Fourth-set failures

### H41: Add three houses with roofs painted blue.

Expected:

```json
[
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

Notices: Unsupported, negated or ambiguous post-noun color; that object instruction was skipped.

### H42: Plant flowers, exactly five of them.

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

Notices: Skipped a context-only or unsupported instruction; use an explicit add/build/plant verb to create objects.

### H43: Build a house with a roof that is yellow.

Expected:

```json
[
  {
    "action": "add",
    "type": "house",
    "count": 1,
    "color": "yellow"
  }
]
```

Actual:

```json
[]
```

Notices: Unsupported, negated or ambiguous post-noun color; that object instruction was skipped.

### H44: Place two small houses and three large ones.

Expected:

```json
[
  {
    "action": "add",
    "type": "house",
    "count": 2,
    "color": null
  },
  {
    "action": "add",
    "type": "house",
    "count": 3,
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
    "count": 2,
    "color": null
  }
]
```

Notices: None.

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

### H46: Plant two trees that are green and three that are yellow.

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
[
  {
    "action": "add",
    "type": "tree",
    "count": 2,
    "color": "green"
  }
]
```

Notices: None.

### H47: Add flowers, five in all.

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

Notices: No supported object or setting found in one clause. Name an object explicitly; pronoun references are not resolved.

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


## Second-set remaining failures

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


## Third-set remaining failures

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

## Reproduce

From the project root:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests
.\.venv\Scripts\python.exe -m tests.evaluate
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --allow-parser-change --output evaluation/heldout_retest_v4.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v2.json --dataset-sha256 050f1f92dba55b89883ebd05c4dc074b287c230a65f33f3d12a7a321ee17042b --allow-parser-change --output evaluation/fresh_v2_retest_v4.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v3.json --dataset-sha256 bc902a965baba135a0b81dc0774230921ed49a82bb510305a771da0e1a684927 --allow-parser-change --output evaluation/fresh_v3_retest_v4.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v4.json --dataset-sha256 83f280f866430ebcabf50de1ac3741a62da42d74757f20fb97db2c675c62a0cd --output evaluation/fresh_results_v4.json
.\.venv\Scripts\python.exe -X utf8 -m evaluation.write_postnoun_report
```

From `frontend/`, with the local servers running: `npm test`, `npm run test:e2e`, `npm run build`.

Labels: `tests/fresh_commands_v4.json`. Complete predictions/notices: `evaluation/fresh_results_v4.json`. Three retests: `evaluation/heldout_retest_v4.json`, `evaluation/fresh_v2_retest_v4.json`, `evaluation/fresh_v3_retest_v4.json`. Regression source: `tests/test_postnoun_fixes.py` and `frontend/tests/browser/smoke.spec.js`.

Parser SHA256: `a3af0d0696f9da20ab3a2863f8851f3f299a20919b9590a341ad7789dbc946e0`.
Backend pipeline SHA256: `60cd2a4974ba8c51b54b4a71b66818ef06be55abada1b75609174aebc8bfbd32`.
Fourth dataset SHA256: `83f280f866430ebcabf50de1ac3741a62da42d74757f20fb97db2c675c62a0cd`.

The frozen dataset records per-file source hashes and the uniqueness-check input hashes. All four evaluations verified the same unchanged backend pipeline before and after prediction. The new dataset builder refuses overwriting labels; fresh evaluation refuses a changed pipeline. Once this sample informs future rule changes, use a separate result file marked as a development retest and a newly frozen sample for another fresh-command claim.
