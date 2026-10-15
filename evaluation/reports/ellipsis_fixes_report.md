# WordWorld quantity, roof-clause and ellipsis fixes — 15 October 2026

**Four saved-set retests: 50/50 (100.0%), 47/50 (94.0%), 45/50 (90.0%), 46/50 (92.0%). Fifth fresh set: 41/50 (82.0%).**

All six targeted errors from the fourth set now pass: H42/H47 (exactly five/five in all), H41/H43 (painted roofs/nested roof clauses), H44 (three large ones), H46 (coordinated relative clauses). There are no new exact-match regressions on the four saved sets. Historical labels and original predictions remain intact.

The fifth set contains 50 newly hand-authored commands, gold actions and scopes frozen before first prediction with backend source hashes. No normalized exact overlaps were found against the five earlier datasets (the development set and four diagnostic sets), Python regression literals, browser test literals or README lines at freeze time. Similar grammar constructions are intentional. The author saw the implementation and earlier errors, so these are diagnostic samples, not independent human-labeled or random real-user benchmarks.

## Implemented behavior

- `exactly` works with explicit whole-number quantities and group quantifiers before nouns and in post-noun appositives. `in all` joins the supported `in total`, `altogether`, and `of them` endings. Counts are read before creation and discourse references. Negative/fractional/ambiguous counts abstain; the existing 16-per-action cap applies.
- Roof-color clauses include `roofs painted blue`, `with a roof that/which is yellow`, `whose roof is painted red`, and `that/which has a blue roof`, with colored/coloured variants. The same bounded grammar maps leaves/foliage and petals onto their existing visible colors. Negated/conflicting colors and unsupported object-part mappings abstain.
- Adjacent counted `one/ones` groups inherit the most recent explicit source noun in the same creation phrase: `two small houses and three large ones` yields separate counts two and three. Only noun type is inherited; omitted color retains the existing default. These create new objects, so they are not ID references to existing objects. Explicit new verbs and intervening placement constraints end this inheritance scope.
- Counted relative continuations such as `two trees that are green and three that are yellow`, including comma lists and `whose roof` clauses, yield separate actions and colors. Their groups remain available to bounded removal and spatial `them` references. A trailing placement applies to the adjacent groups under the documented shared-placement grammar.
- Highlights retain exact original offsets, including quantities/colors and inherited `ones` as an object span. Per-group zero counts and negation skip only that group. Numeric conjunctions and hyphenated cardinals remain intact. Unresolved inherited nouns produce notices; a following landmark must not become an unintended creation.

Small/large/tall/short describe groups only; sprite sizes are not changed or scored. Action grounding is deterministic and rule based; spaCy supplies annotations. No backend rules or frozen labels were changed after observing fifth-set predictions.

## Verification

| Check | Result |
|---|---|
| Python parser/API tests | 280 passed; 57 added regression cases |
| Original development 50 | 50/50 exact action matches |
| Scene/preview unit tests | 16 passed |
| Desktop/mobile Chromium checks | 20 passed |
| React production build | Passed |
| Live API through Vite | Exactly five flowers returns count 5 |

The browser flow checks five actual added flowers, purple/blue roofs across an inherited-noun group, separate yellow/pink tree groups anchoring a flower between them, exact inline highlights, and removal of newly introduced house groups while preserving older houses. Existing manipulation, undo/redo, autosave, weather and offline-preview checks also pass. Screenshots: `.runtime/ellipsis-fixes-desktop.png` and `.runtime/ellipsis-fixes-mobile.png`.

The long-running backend initially served the previous parser despite file changes. Restarting the WordWorld FastAPI process restored the current rules; it now watches only `backend/`, avoiding reloads from test/report/backup files. The failed browser run was diagnosed from live API predictions, then the full desktop/mobile suite was rerun successfully. Vite and FastAPI remain running.

## Evaluations

| Set | Previous round | Current round | Interpretation |
|---|---:|---:|---|
| Diagnostic set 1 | 50/50 (100.0%) | 50/50 (100.0%) | Same gold labels; development retest |
| Diagnostic set 2 | 47/50 (94.0%) | 47/50 (94.0%) | Same gold labels; development retest |
| Diagnostic set 3 | 45/50 (90.0%) | 45/50 (90.0%) | Same gold labels; development retest |
| Diagnostic set 4 | 40/50 (80.0%) | 46/50 (92.0%) | Same gold labels; development retest |
| Fifth fresh set | Not previously executed | 41/50 (82.0%) | Gold and code frozen before prediction |

| Per-command metric | Set 1 | Set 2 | Set 3 | Set 4 | Fresh set 5 |
|---|---:|---:|---:|---:|---:|
| Intent sequence | 50/50 (100.0%) | 47/50 (94.0%) | 45/50 (90.0%) | 47/50 (94.0%) | 43/50 (86.0%) |
| Objects/counts/colors | 50/50 (100.0%) | 48/50 (96.0%) | 46/50 (92.0%) | 47/50 (94.0%) | 42/50 (84.0%) |
| Spatial fields, gold-spatial subset | 22/22 (100.0%) | 18/19 (94.7%) | 18/21 (85.7%) | 12/13 (92.3%) | 7/8 (87.5%) |
| Settings, gold-setting subset | 6/6 (100.0%) | 4/5 (80.0%) | 3/4 (75.0%) | 1/2 (50.0%) | 1/2 (50.0%) |

Fresh scopes: **40/40 core and 1/10 broader probes**. Core includes zero/negated count groups and one reset-reference refusal. Probes test broader intended English beyond adjacent-group grammar. Different distributions prevent interpreting the new fresh score as a paired improvement over an earlier sample.

Exact match compares every field of every ordered action dictionary. Field metrics are per-command sequences, not token scores. The object metric includes matching empty typed-action lists for pure settings. Spatial/setting metrics use gold-bearing subsets; geometry, scene manipulation and cross-request context are outside parser accuracy.

## Remaining errors and next priorities

The fifth set has **9 errors and no exceptions**. Four failures (J41, J45, J48, J50) emit wrong or partial actions without notices. The extra default object in J41 is the highest-priority remaining creation error.

| Pattern | Cases | Actual behavior |
|---|---|---|
| Counted partitions after a bare plural | J41 | `trees, two that are green and three that are yellow` adds an extra uncolored tree before the requested two groups: six trees instead of five, without notice. |
| Passive roof clause | J43 | `whose roof has been painted red` abstains with a notice. |
| Shorter quantity ending | J44 | `flowers, five total` creates one flower and reports an unsupported second clause. |
| Predicate ellipsis | J45 | `and three yellow` loses the second group without notice. |
| Partitioned roof groups | J46 | `two houses, one with a blue roof and one with a green roof` abstains instead of splitting the total into two colored houses. |
| Cross-clause noun-type inheritance | J47 | `add three large ones behind the tower` loses the new group with notices; the tower is correctly not created. |
| Group multiplication | J48 | `three groups of two` creates one castle instead of six, without notice. |
| Subordinate creation | J49 | Preservation swallows `while adding two blue houses`; no houses are added. |
| Setting paraphrase | J50 | `daylight` is missed; snow clearing works, without a notice for the missing time change. |

J42 passes: `exactly five blue-roofed cottages` produces five blue houses. This verifies that wording, not general compound-adjective understanding.

The four saved sets retain twelve errors: F35/F48/F50, G43–G47, and H45/H48/H49/H50. They cover daylight, construct, subordinate creation, finite relation/direction paraphrases, group multiplication and weather paraphrases. Full predictions and notices follow below.

## All 50 new commands

| ID | Scope | Result | Command |
|---|---|---|---|
| J01 | core | PASS | Add flowers, exactly eight in all. |
| J02 | core | PASS | Plant trees, exactly a pair in all. |
| J03 | core | PASS | Place cottages, exactly eleven of them. |
| J04 | core | PASS | Add boulders, exactly half a dozen in total. |
| J05 | core | PASS | Create towers, exactly three in all. |
| J06 | core | PASS | Build bridges, exactly two of them across the stream. |
| J07 | core | PASS | Add flowers, exactly eighteen in all. |
| J08 | core | PASS | Create exactly four white flowers near the castle. |
| J09 | core | PASS | Build three homes with roofs painted pink. |
| J10 | core | PASS | Place a cabin with a roof which is painted green. |
| J11 | core | PASS | Add a cottage whose roof is coloured white. |
| J12 | core | PASS | Build a home which has an orange roof. |
| J13 | core | PASS | Add a house with roofs that are painted red. |
| J14 | core | PASS | Plant two trees with leaves painted purple. |
| J15 | core | PASS | Place three flowers with petals which are blue. |
| J16 | core | PASS | Build a house with a roof that is yellow and two trees with green foliage. |
| J17 | core | PASS | Place three small towers and two large ones. |
| J18 | core | PASS | Draw two short bridges and a tall one over the creek. |
| J19 | core | PASS | Add a rock and three small ones. |
| J20 | core | PASS | Plant four trees and a pair of blue ones. |
| J21 | core | PASS | Build two white cottages and one pink one. |
| J22 | core | PASS | Add two tiny castles, three big ones, and a little one. |
| J23 | core | PASS | Place two flowers and four purple ones beside the castle. |
| J24 | core | PASS | Build one house and zero big ones. |
| J25 | core | PASS | Build no homes and three yellow ones. |
| J26 | core | PASS | Plant three trees that are pink and two which are blue. |
| J27 | core | PASS | Add one house whose roof is white and two whose roofs are orange. |
| J28 | core | PASS | Place four flowers that are yellow, two that are pink, and three that are white. |
| J29 | core | PASS | Build two cottages with blue roofs and one whose roof is painted purple. |
| J30 | core | PASS | Plant two trees that are green and not four that are yellow. |
| J31 | core | PASS | Create one house and one whose roof is painted red near the lake. |
| J32 | core | PASS | Add two trees with pink leaves and three blue ones. |
| J33 | core | PASS | Build one pink house and one blue one; put a flower between them. |
| J34 | core | PASS | Add flowers, exactly seven in all; remove two of them; remove them. |
| J35 | core | PASS | Build three houses with red roofs and two large ones; remove them. |
| J36 | core | PASS | Near the castle, build a house with a roof which is green and two large ones. |
| J37 | core | PASS | Preserve the flowers; add trees, exactly five in all; make it night. |
| J38 | core | PASS | Grow two trees that are green and three that are purple; remove two of them. |
| J39 | core | PASS | Don’t add cottages with roofs painted red; add flowers, exactly four in total. |
| J40 | core | PASS | Build a house with a blue roof; reset; remove it. |
| J41 | capability_probe | FAIL | Add trees, two that are green and three that are yellow. |
| J42 | capability_probe | PASS | Build exactly five blue-roofed cottages. |
| J43 | capability_probe | FAIL | Build a house whose roof has been painted red. |
| J44 | capability_probe | FAIL | Add flowers, five total. |
| J45 | capability_probe | FAIL | Plant two trees that are green and three yellow. |
| J46 | capability_probe | FAIL | Place two houses, one with a blue roof and one with a green roof. |
| J47 | capability_probe | FAIL | Build two cottages near the lake; add three large ones behind the tower. |
| J48 | capability_probe | FAIL | Create castles in three groups of two. |
| J49 | capability_probe | FAIL | Keep the flowers while adding two blue houses. |
| J50 | capability_probe | FAIL | Make it daylight and stop the snow. |

## Fresh fifth-set failures

### J41: Add trees, two that are green and three that are yellow.

Gold rationale: A bare plural followed by counted descriptions specifies the complete collection; do not add an extra default tree.

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
    "count": 1,
    "color": null
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
    "count": 3,
    "color": "yellow"
  }
]
```

Notices: None.

### J43: Build a house whose roof has been painted red.

Expected:

```json
[
  {
    "action": "add",
    "type": "house",
    "count": 1,
    "color": "red"
  }
]
```

Actual:

```json
[]
```

Notices: Unsupported, negated or ambiguous post-noun color; that object instruction was skipped.

### J44: Add flowers, five total.

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

### J45: Plant two trees that are green and three yellow.

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

### J46: Place two houses, one with a blue roof and one with a green roof.

Gold rationale: The two later groups partition the explicit total of two houses; no extra default group is requested.

Expected:

```json
[
  {
    "action": "add",
    "type": "house",
    "count": 1,
    "color": "blue"
  },
  {
    "action": "add",
    "type": "house",
    "count": 1,
    "color": "green"
  }
]
```

Actual:

```json
[]
```

Notices: An inherited noun group needs explicit, unambiguous counts and supported modifiers; that object instruction was skipped.

### J47: Build two cottages near the lake; add three large ones behind the tower.

Gold rationale: Natural-English noun-type inheritance across an explicit new verb is broader than the documented adjacent-group contract; gold requests houses, never a new tower.

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


## Saved set 2 remaining failures

### F35: Do not make it midnight; make it daylight.

Gold rationale: Daylight denotes day, but is a new lexical setting paraphrase rather than a documented keyword.

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

Gold rationale: The gerund adding introduces a second intended operation after a preservation clause.

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

Gold rationale: Construct is a new creation-verb paraphrase.

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

Gold rationale: The finite verb crosses paraphrases across; expected output does not request a second river.

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

## Reproduce

From the project root:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests
.\.venv\Scripts\python.exe -m tests.evaluate
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --allow-parser-change --output evaluation/results/heldout_retest_v5.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v2.json --dataset-sha256 050f1f92dba55b89883ebd05c4dc074b287c230a65f33f3d12a7a321ee17042b --allow-parser-change --output evaluation/results/fresh_v2_retest_v5.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v3.json --dataset-sha256 bc902a965baba135a0b81dc0774230921ed49a82bb510305a771da0e1a684927 --allow-parser-change --output evaluation/results/fresh_v3_retest_v5.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v4.json --dataset-sha256 83f280f866430ebcabf50de1ac3741a62da42d74757f20fb97db2c675c62a0cd --allow-parser-change --output evaluation/results/fresh_v4_retest_v5.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v5.json --dataset-sha256 e20bbe0ba47f12431c33708b4aa653ce8689a2b9027aca7294747dc0c0f9bc8e --output evaluation/results/fresh_results_v5.json
.\.venv\Scripts\python.exe -X utf8 -m evaluation.scripts.write_ellipsis_report
```

From `frontend/`, with FastAPI and Vite running: `npm test`, `npm run test:e2e`, `npm run build`.

Frozen labels: `tests/fresh_commands_v5.json`. Predictions/notices/metrics: `evaluation/results/fresh_results_v5.json`. Regressions: `tests/test_ellipsis_fixes.py`, `frontend/tests/browser/smoke.spec.js`.

Parser SHA256: `23fd7136e3f65ebf637aadbdfadb89188e8b4d5c8216125dcd65445dd25ab731`.
Backend pipeline SHA256: `a2eb230316fdf1befedbe7f1c090d9497361d281d57d3214b362b603dea6595a`.
Fifth dataset SHA256: `e20bbe0ba47f12431c33708b4aa653ce8689a2b9027aca7294747dc0c0f9bc8e`.

All five evaluations verified the same backend source fingerprint before and after prediction. Frozen input hashes and gold labels are preserved. After these new errors inform future development, reruns need separate comparison outputs and a newly frozen sample for another fresh-command claim.
