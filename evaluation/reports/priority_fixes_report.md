# WordWorld priority fixes and fresh evaluation — 15 October 2026

**Original diagnostic set: 35/50 → 46/50 (70% → 92%). Second fresh set: 40/50 (80%).**

The original 50-command set is now a development/regression comparison set. Its gold labels and original 35/50 results were preserved; its retest is not an unseen-language result. The second set contains 50 newly authored commands with expected outputs frozen before their first execution on the final parser. There are no normalized exact overlaps with either previous 50-command set, Python regression string literals, browser smoke test strings, or README command lines.

Both sets are hand-authored diagnostic samples. Their author saw the implementation and previous results; they are neither independently human-labeled nor randomly sampled from real users. They intentionally include broader capability probes. The old and new distributions differ, so 92% and 80% are not a paired before/after comparison. No parser changes or gold-label adjustments were made after observing second-round predictions.

## Implemented fixes

- Normalize curly apostrophes, common Unicode hyphens, and Unicode minus signs one character at a time, keeping original text offsets exact. Negated creation/removal/reset clauses are skipped; `not rain`, `not snow`, and `without rain/snow` map to clear weather.
- Treat keep/leave/preserve/retain/protect clauses as non-mutating object mentions. Unsupported context/verb statements no longer imply creation merely because they mention a supported noun. Bare noun phrases remain supported.
- Parse common cardinal words, pairs, dozens, half a dozen, and group multipliers. Enforce the 16-object action cap. Negative, fractional, disjunctive and recognized ambiguous quantities produce a notice instead of defaulting silently to one.
- Attach initial location phrases to the following explicit action, with or without a comma. Extract their landmarks before considering action subjects, including two-target `between`. A shared initial phrase applies to coordinated subjects under one verb; an explicit new verb starts a new instruction. Unsupported filtered removal and multiple placement constraints are skipped with notices.
- Highlight preserved object mentions in the inline explanation; make no-change responses explicit. Action grounding remains rule based; spaCy supplies token/grammar annotations.

## Verification

| Check | Result |
|---|---|
| Python parser/API regressions | 142 passed; 64 more than the original 78 |
| Original 50-command development set | 50/50 exact matches |
| Scene and offline-preview logic | 13 passed |
| Desktop/mobile Playwright | 14 passed; includes negation, protected mentions, quantity phrases and initial-location rendering |
| React production build | Passed |

The new browser flow checks that a negated bridge command leaves the count unchanged, preserving houses/removing flowers keeps exactly two houses, and `Behind the lake, plant a pair of purple trees` adds two trees without adding a second lake. Screenshots are saved at `.runtime/parser-fixes-desktop.png` and `.runtime/parser-fixes-mobile.png`.

## Accuracy

| Metric | Original parser, first set | Updated parser, first-set retest | Updated parser, second fresh set |
|---|---:|---:|---:|
| Full ordered action JSON | 35/50 (70.0%) | 46/50 (92.0%) | 40/50 (80.0%) |
| Intent sequence | 39/50 (78.0%) | 46/50 (92.0%) | 41/50 (82.0%) |
| Objects/counts/colors, all commands | 36/50 (72.0%) | 46/50 (92.0%) | 41/50 (82.0%) |
| Spatial fields, gold-spatial subset | 18/22 (81.8%) | 21/22 (95.5%) | 15/19 (78.9%) |
| Time/weather values, gold-setting subset | 5/6 (83.3%) | 6/6 (100.0%) | 4/5 (80.0%) |

The first-set core subset improved from **35/44 to 44/44**. Its six capability probes improved from 0/6 to 2/6 after preservation/context handling was fixed. All four remaining first-set errors are H30–H32 (pronouns) and H38 (elliptical coordination).

The second fresh set scored **40/40 core commands** and **0/10 broader capability probes**. Four failed commands emitted no parser notice. There were no parser exceptions. Counts clipped to 16 and invalid-quantity abstentions were labeled according to the existing action contract, before prediction.

Metrics are per-command sequence comparisons. Exact match compares every action field and action order. The object metric includes matching empty object lists on pure-setting/no-op commands. Spatial and setting scores use their gold-bearing subsets. Existing landmarks are assumed; scene geometry and cross-request conversation state are not part of parser accuracy.

## Remaining errors from the second fresh set

| Priority | Pattern / cases | Observed behavior | Next fix |
|---|---|---|---|
| 1 | Unsupported relation paraphrase — F47 | `Put a bridge spanning the creek.` adds a bridge AND an unintended river; relation/target are missing. | Classify noun roles conservatively within each action and recognize relational paraphrases such as spanning, or abstain on unsupported modifiers. The current fixes do not guarantee absence of unintended creation for every English construction. |
| 2 | Pronouns — F41–F43 | `it` and `them` lose the following placement/removal action. | Add scoped, typed reference resolution within an utterance. |
| 3 | Omitted coordinated nouns — F44–F45 | Two differently colored groups collapse to the last group. | Expand coordinated count/color phrases into separate grounded actions. |
| 4 | Post-noun attributes — F46 | `a house with a blue roof` loses blue. | Attach roof/color modifiers to the house rather than requiring color before the noun. |
| 4 | Clause/verb paraphrases — F48, F50 | `while adding` loses the add action; `construct` abstains. | Recognize action-bearing subordinate clauses and expand safe verb aliases. |
| 5 | Setting paraphrase — F35 | `daylight` does not set day. | Expand setting aliases while preserving negation scope. |

## All 50 second-round commands

| ID | Scope | Result | Command |
|---|---|---|---|
| F01 | core | PASS | Please don’t plant a forest next to the castle. |
| F02 | core | PASS | Never erase the bridges or the roads. |
| F03 | core | PASS | Don‘t build six yellow cabins. |
| F04 | core | PASS | Keep the pond and add three pink blossoms. |
| F05 | core | PASS | Protect the cottages; delete two rocks. |
| F06 | core | PASS | Leave all mountains alone, then show a lighthouse. |
| F07 | core | PASS | Do not reset the map; insert a road. |
| F08 | core | PASS | Don’t add flowers, rocks, or trees; build a blue tower. |
| F09 | core | PASS | Retain the forest and remove a bridge. |
| F10 | core | PASS | Avoid the river and create a small castle. |
| F11 | core | PASS | Build thirteen white cottages. |
| F12 | core | PASS | Plant fourteen green trees near the bridge. |
| F13 | core | PASS | Add fifteen pink blossoms. |
| F14 | core | PASS | Create a dozen red homes beside the path. |
| F15 | core | PASS | Put two pairs of rocks west of the pond. |
| F16 | core | PASS | Grow half a dozen trees behind the fortress. |
| F17 | core | PASS | Place sixteen orange flowers inside the castle. |
| F18 | core | PASS | Build eighteen huts. |
| F19 | core | PASS | Plant three dozen flowers. |
| F20 | core | PASS | Add twenty‑two stones. |
| F21 | core | PASS | North of the bridge, plant three trees. |
| F22 | core | PASS | In front of the tower, place five pink flowers. |
| F23 | core | PASS | Across the stream, build a bridge. |
| F24 | core | PASS | Within the fortress, put two rocks. |
| F25 | core | PASS | Between the lake and the mountain, create a road. |
| F26 | core | PASS | Between two cottages, plant four trees. |
| F27 | core | PASS | Close to the castle, build a house and a tower. |
| F28 | core | PASS | To the right of the lake place three red cabins. |
| F29 | core | PASS | Beside the road, do not add any trees. |
| F30 | core | PASS | Near the lake, build three cottages and two towers. |
| F31 | core | PASS | Make it nighttime without snow. |
| F32 | core | PASS | Make it not snowing. |
| F33 | core | PASS | Stop snowing and make it morning. |
| F34 | core | PASS | Make it sunny; make it rain; stop the rain. |
| F35 | capability_probe | FAIL | Do not make it midnight; make it daylight. |
| F36 | core | PASS | Remove zero towers, then add eleven blue flowers. |
| F37 | core | PASS | Build a house and never remove it. |
| F38 | core | PASS | Place −2 rocks by the lake. |
| F39 | core | PASS | Add 1.5 bridges over the river. |
| F40 | core | PASS | Build two or four cottages. |
| F41 | capability_probe | FAIL | Create a tower and put two trees behind it. |
| F42 | capability_probe | FAIL | Plant three flowers and remove one of them. |
| F43 | capability_probe | FAIL | Build a lake and a castle, then add a road between them. |
| F44 | capability_probe | FAIL | Place two red and three yellow houses. |
| F45 | capability_probe | FAIL | Plant one pink and one purple flower. |
| F46 | capability_probe | FAIL | Add a house with a blue roof. |
| F47 | capability_probe | FAIL | Put a bridge spanning the creek. |
| F48 | capability_probe | FAIL | Leave the houses untouched while adding a lake. |
| F49 | core | PASS | To the north of the lake, add a house. |
| F50 | capability_probe | FAIL | Construct two red cottages next to the pond. |

## Expected and actual outputs for fresh-set errors

### F35: Do not make it midnight; make it daylight.

Category: setting_paraphrase. Scope: capability_probe.

Label rationale: Daylight denotes day, but is a new lexical setting paraphrase rather than a documented keyword.

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

Notices: Skipped a negated instruction; no objects were changed for that clause.; No supported object or setting found in one clause. Name an object explicitly; pronoun references are not resolved.

### F41: Create a tower and put two trees behind it.

Category: coreference. Scope: capability_probe.

Expected:

```json
[
  {
    "action": "add",
    "type": "tower",
    "count": 1,
    "color": null
  },
  {
    "action": "add",
    "type": "tree",
    "count": 2,
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
    "type": "tower",
    "count": 1,
    "color": null
  }
]
```

Notices: A spatial instruction needs named landmarks; use 'between two houses' or 'between the house and the lake'.

### F42: Plant three flowers and remove one of them.

Category: coreference. Scope: capability_probe.

Expected:

```json
[
  {
    "action": "add",
    "type": "flower",
    "count": 3,
    "color": null
  },
  {
    "action": "remove",
    "type": "flower",
    "count": 1
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

Notices: No supported object or setting found in one clause. Name an object explicitly; pronoun references are not resolved.

### F43: Build a lake and a castle, then add a road between them.

Category: coreference. Scope: capability_probe.

Expected:

```json
[
  {
    "action": "add",
    "type": "lake",
    "count": 1,
    "color": null
  },
  {
    "action": "add",
    "type": "castle",
    "count": 1,
    "color": null
  },
  {
    "action": "add",
    "type": "road",
    "count": 1,
    "color": null,
    "relation": "between",
    "target": "lake",
    "targets": [
      "lake",
      "castle"
    ]
  }
]
```

Actual:

```json
[
  {
    "action": "add",
    "type": "lake",
    "count": 1,
    "color": null
  },
  {
    "action": "add",
    "type": "castle",
    "count": 1,
    "color": null
  }
]
```

Notices: A spatial instruction needs named landmarks; use 'between two houses' or 'between the house and the lake'.

### F44: Place two red and three yellow houses.

Category: coordination_ellipsis. Scope: capability_probe.

Expected:

```json
[
  {
    "action": "add",
    "type": "house",
    "count": 2,
    "color": "red"
  },
  {
    "action": "add",
    "type": "house",
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
    "type": "house",
    "count": 3,
    "color": "yellow"
  }
]
```

Notices: None.

### F45: Plant one pink and one purple flower.

Category: coordination_ellipsis. Scope: capability_probe.

Expected:

```json
[
  {
    "action": "add",
    "type": "flower",
    "count": 1,
    "color": "pink"
  },
  {
    "action": "add",
    "type": "flower",
    "count": 1,
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
    "count": 1,
    "color": "purple"
  }
]
```

Notices: None.

### F46: Add a house with a blue roof.

Category: postposed_attributes. Scope: capability_probe.

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

### F47: Put a bridge spanning the creek.

Category: relation_paraphrase. Scope: capability_probe.

Label rationale: Spanning paraphrases across; creek is an existing landmark, not a requested new river.

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
[
  {
    "action": "add",
    "type": "bridge",
    "count": 1,
    "color": null
  },
  {
    "action": "add",
    "type": "river",
    "count": 1,
    "color": null
  }
]
```

Notices: None.

### F48: Leave the houses untouched while adding a lake.

Category: clause_paraphrase. Scope: capability_probe.

Label rationale: The gerund adding introduces a second intended operation after a preservation clause.

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

Category: verb_paraphrase. Scope: capability_probe.

Label rationale: Construct is a new creation-verb paraphrase.

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

## Reproduce

From the project root:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --allow-parser-change --output evaluation/results/heldout_retest.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v2.json --dataset-sha256 050f1f92dba55b89883ebd05c4dc074b287c230a65f33f3d12a7a321ee17042b --output evaluation/results/fresh_results_v2.json
.\.venv\Scripts\python.exe -X utf8 evaluation/scripts/write_priority_report.py
```

From `frontend/`, with API and Vite running: `npm test`, `npm run test:e2e`, and `npm run build`.

- Original frozen labels: `tests/heldout_commands.json` (unchanged).
- Original predictions: `evaluation/results/heldout_results.json` (unchanged).
- First-set retest: `evaluation/results/heldout_retest.json`.
- New frozen labels and development-input hashes: `tests/fresh_commands_v2.json`.
- New predictions/notices: `evaluation/results/fresh_results_v2.json`.
- Regression coverage: `tests/test_accuracy_fixes.py` and `frontend/tests/browser/smoke.spec.js`.

Final parser SHA256: `2484fbb06e7bd322efdb8fe7b242bdae6ff0239940f897ad72f1d47fd43355b9`.
Second-set SHA256: `050f1f92dba55b89883ebd05c4dc074b287c230a65f33f3d12a7a321ee17042b`.

The parser hash is identical between the first-set retest and the second-set run, and before/after the fresh evaluation. The evaluator refuses modified labels and protects the original result file. If second-round failures guide future development, this set becomes a regression/comparison set; another new sample is needed for a future fresh-command claim.
