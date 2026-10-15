# WordWorld reference and coordination fixes — 15 October 2026

**First-set retest: 50/50 (100.0%). Second-set retest: 46/50 (92.0%). Third fresh set: 41/50 (82.0%).**

The previously evaluated sets are now regression/comparison sets. Their labels and original results were preserved. The third set contains 50 new commands and expected outputs frozen before any predictions, with no normalized exact overlap against all three previous sets, regression-test literals, browser smoke-test literals or README command lines. Similar grammar structures are intentionally represented.

These are hand-authored diagnostic samples, not random real-user accuracy estimates or independently human-labeled benchmarks. The author saw the implementation and previous errors. The third set has 40 preassigned core cases and 10 broader grammar probes; some core cases intentionally expect conservative refusal of ambiguous or exhausted references. No parser/rule/label changes were made after observing the third-set results.

## What changed

- `spanning` and `crossing` ground to `across`. Their following nouns are landmarks. Unsupported connections between object nouns reject the instruction instead of creating extra nouns. The exact extra-river regression now emits only one bridge action with river as its target.
- A new request-local reference context tracks creation groups, types, live counts and the action that introduced each group. `it` resolves the latest live singular introduction; `them` resolves the latest coordinated creation collection. Explicit new creation verbs reset collection focus; comma-separated subjects remain one collection. Settings preserve the referents; reset clears them. There is no cross-request or global conversation memory.
- Pronouns support removal subjects and spatial landmarks. Partial removal of a homogeneous collection is bounded to that collection; subsequent pronouns see the remaining count. A partial selection from mixed types or singular `it` after a plural group abstains with a notice. Spatial `them` currently requires exactly two objects with `between`; other plural-spatial relations abstain.
- Explicitly counted coordinated colors expand into separate actions, including comma lists, shared placement relations, group quantifiers and per-group negation. Number phrases such as `one hundred and two` retain their numeric conjunction. Ambiguous color coordination without separate counts abstains. Non-color coordination remains a limitation.
- API `bindings` connect reference actions to their antecedent action indices. The frontend binds these to the actual new SVG object IDs, preserving unrelated older objects, including when the scene limit blocks a creation. Existing named-landmark behavior is unchanged. The action dictionaries remain compatible with the prior schema.
- The inline explanation highlights references and displays their resolved types/counts. Action grounding remains deterministic and rule based; spaCy provides linguistic annotations.

## Verification

| Check | Result |
|---|---|
| Python parser/API regressions | 170 passed (28 additional cases) |
| Original development 50 | 50/50 exact action matches |
| Scene/preview tests | 16 passed, including reference ID/capacity guards |
| Desktop/mobile Playwright | 16 passed |
| React production build | Passed |

The new browser flow checks that a bridge spanning a creek adds no river, a newly built then removed house does not remove the two starter houses, and two coordinated colored houses become the anchors of a tree placed between them. Screenshots: `.runtime/reference-fixes-desktop.png` and `.runtime/reference-fixes-mobile.png`.

## Evaluations

| Set | Before this round | After this round | Interpretation |
|---|---:|---:|---|
| First diagnostic set | 46/50 (92.0%) | 50/50 (100.0%) | Same gold labels; development retest |
| Second diagnostic set | 40/50 (80.0%) | 46/50 (92.0%) | Same gold labels; development retest |
| Third fresh set | Not previously executed | 41/50 (82.0%) | Gold frozen before first prediction |

| Per-command metric | First-set retest | Second-set retest | Third fresh set |
|---|---:|---:|---:|
| Intent sequence | 50/50 (100.0%) | 47/50 (94.0%) | 44/50 (88.0%) |
| Objects/counts/colors | 50/50 (100.0%) | 47/50 (94.0%) | 42/50 (84.0%) |
| Spatial fields, gold-spatial subset | 22/22 (100.0%) | 18/19 (94.7%) | 18/21 (85.7%) |
| Time/weather, gold-setting subset | 6/6 (100.0%) | 4/5 (80.0%) | 3/4 (75.0%) |

First-set scopes: 44/44 core and 6/6 probes. Second-set scopes: 40/40 core and 6/10 probes. Third-set scopes: **40/40 core and 1/10 probes**. Different sets have different distributions; the third-set score is not a paired before/after comparison.

Exact match compares every field in every ordered action dictionary. Field metrics compare per-command sequences, not tokens. The object metric includes matching empty typed-action lists in pure-setting/no-op cases. Spatial/setting metrics use their gold-bearing subsets. Existing named landmarks are assumed; scene geometry and cross-request conversational reference are not part of parser accuracy.

## Remaining errors

The second set still fails F35 (`daylight`), F46 (post-noun roof color), F48 (`while adding`) and F50 (`construct`). These were not part of the current requested grammar changes.

The third set has **9 exact-match errors and no parser exceptions**. Four errors emitted no parser notice. The unsupported finite relation `that crosses the river` and direction `east side of the lake` now abstain rather than create their landmarks.

| Pattern | Third-set cases | Example / behavior |
|---|---|---|
| Post-noun attributes | G41–G42 | `a cottage with an orange roof` loses orange. |
| Relation/direction paraphrases | G43, G47 | `that crosses` and `east side of` abstain; no extra river/lake is created. |
| Creation/subordinate verb variants | G44–G45 | `construct` and `while building` lose the intended creation. |
| Negated weather with a determiner | G46 | `without any rain` fails to clear weather; only day is applied. |
| Quantity after the noun | G49 | `houses, three of them` creates one house instead of three. |
| Coordination without colors | G50 | `two small and three large houses` keeps only the final three. |

G48 passed: `those trees` explicitly names the object type and produces the correct two-target action. This does not establish general demonstrative or color-filtered reference support.

## All 50 new commands

| ID | Scope | Result | Command |
|---|---|---|---|
| G01 | core | PASS | Add two bridges spanning the stream. |
| G02 | core | PASS | Place a road crossing the creek. |
| G03 | core | PASS | Draw a bridge spanning the river and three red cottages. |
| G04 | core | PASS | Build a bridge spanning the creek; plant four trees behind it. |
| G05 | core | PASS | Don’t build bridges crossing the stream; add a tower. |
| G06 | core | PASS | Create a castle, then put a tree to the left of it. |
| G07 | core | PASS | Build three red cottages; remove two of them. |
| G08 | core | PASS | Plant four flowers; remove one of them; remove them. |
| G09 | core | PASS | Make a tower and a cottage; place a rock between them. |
| G10 | core | PASS | Add two lakes; put a bridge between them. |
| G11 | core | PASS | Create a road; make it night; plant two trees near it. |
| G12 | core | PASS | Add a rock; remove it; remove it again. |
| G13 | core | PASS | Build a house, a tower, and a castle; remove them. |
| G14 | core | PASS | Create six trees; erase twenty of them. |
| G15 | core | PASS | Add two rocks; never remove them. |
| G16 | core | PASS | Build a cottage and a tower; delete one of them. |
| G17 | core | PASS | Plant three trees; remove it. |
| G18 | core | PASS | Remove them; add a lake. |
| G19 | core | PASS | Build a house; reset; put a flower near it. |
| G20 | core | PASS | Create one white and one orange house; add a flower between them. |
| G21 | core | PASS | Add two green and four purple trees. |
| G22 | core | PASS | Build a yellow and a pink cottage. |
| G23 | core | PASS | Place three white, two blue, and one purple flower. |
| G24 | core | PASS | Plant a pair of yellow and three pink flowers. |
| G25 | core | PASS | Build two red and not three blue cottages. |
| G26 | core | PASS | Near the tower, plant one pink and one white flower. |
| G27 | core | PASS | Add two blue and three red houses behind the lake. |
| G28 | core | PASS | Create one green and one yellow tree; remove them. |
| G29 | core | PASS | Put one purple and one pink flower beside the castle, then remove it. |
| G30 | core | PASS | Build two red houses and one blue house; put a rock behind it. |
| G31 | core | PASS | Keep the lake; add fourteen white flowers. |
| G32 | core | PASS | Don’t create any castles; build a bridge spanning the stream. |
| G33 | core | PASS | South of the tower, place a dozen pink flowers. |
| G34 | core | PASS | Build one hundred and three blue cottages. |
| G35 | core | PASS | Clear everything; add a river; build a bridge spanning it. |
| G36 | core | PASS | Make it rain and then stop raining; create a rock. |
| G37 | core | PASS | Build zero red and one green house. |
| G38 | core | PASS | Add a tree; make it day; remove it. |
| G39 | core | PASS | Beside the castle, add a pair of orange flowers and a red house. |
| G40 | core | PASS | Build a tower; remove it; add two blue flowers. |
| G41 | capability_probe | FAIL | Build a cottage with an orange roof. |
| G42 | capability_probe | FAIL | Place a house whose roof is green. |
| G43 | capability_probe | FAIL | Build a bridge that crosses the river. |
| G44 | capability_probe | FAIL | Construct three white homes near the river. |
| G45 | capability_probe | FAIL | Keep the trees untouched while building a house. |
| G46 | capability_probe | FAIL | Make it day without any rain. |
| G47 | capability_probe | FAIL | Add a house to the east side of the lake. |
| G48 | capability_probe | PASS | Plant two trees and put a flower between those trees. |
| G49 | capability_probe | FAIL | Build houses, three of them. |
| G50 | capability_probe | FAIL | Place two small and three large houses. |

## Fresh-set failures: expected and actual

### G41: Build a cottage with an orange roof.

Category: postposed_attributes. Scope: capability_probe.

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

### G42: Place a house whose roof is green.

Category: postposed_attributes. Scope: capability_probe.

Expected:

```json
[
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

### G43: Build a bridge that crosses the river.

Category: relation_paraphrase. Scope: capability_probe.

Label rationale: The finite verb crosses paraphrases across; expected output does not request a second river.

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

Category: verb_paraphrase. Scope: capability_probe.

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

Category: clause_paraphrase. Scope: capability_probe.

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

Category: negated_setting_paraphrase. Scope: capability_probe.

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

Category: direction_paraphrase. Scope: capability_probe.

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

### G49: Build houses, three of them.

Category: postposed_quantity. Scope: capability_probe.

Expected:

```json
[
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
    "count": 1,
    "color": null
  }
]
```

Notices: Object pronouns can be removal subjects or spatial landmarks; no object was created from this reference.

### G50: Place two small and three large houses.

Category: coordination_without_colors. Scope: capability_probe.

Label rationale: Score distinct coordinated count groups using existing action fields; size rendering is not scored.

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
    "count": 3,
    "color": null
  }
]
```

Notices: None.

## Reproduce

From the project root:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --allow-parser-change --output evaluation/results/heldout_retest_v3.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v2.json --dataset-sha256 050f1f92dba55b89883ebd05c4dc074b287c230a65f33f3d12a7a321ee17042b --allow-parser-change --output evaluation/results/fresh_v2_retest_v3.json
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout --dataset tests/fresh_commands_v3.json --dataset-sha256 bc902a965baba135a0b81dc0774230921ed49a82bb510305a771da0e1a684927 --output evaluation/results/fresh_results_v3.json
.\.venv\Scripts\python.exe -X utf8 -m evaluation.scripts.write_reference_report
```

From `frontend/`, with FastAPI and Vite running: `npm test`, `npm run test:e2e`, `npm run build`.

- Third frozen labels: `tests/fresh_commands_v3.json`.
- Third predictions, notices and per-case correctness: `evaluation/results/fresh_results_v3.json`.
- Earlier-set retests: `evaluation/results/heldout_retest_v3.json`, `evaluation/results/fresh_v2_retest_v3.json`.
- Main regressions: `tests/test_reference_fixes.py`, `frontend/tests/world.test.js`, `frontend/tests/browser/smoke.spec.js`.

Parser SHA256: `ebd28a8e790143913c5d52db10af0de1b02e5db3dd42841c48f83e5f9dee7ec0`.
Backend pipeline SHA256: `3846424e07c0a52fcae4d73473603065f1d038a83404fc5ca361d4b14798eba4`.
Third dataset SHA256: `bc902a965baba135a0b81dc0774230921ed49a82bb510305a771da0e1a684927`.

All backend Python source hashes, including the new reference module, were captured before and after each evaluation. The evaluator refuses changed labels/pipeline for a fresh run and protects historical baseline results. Once third-set errors guide future development, it becomes a regression/comparison set and a new sample is needed for another fresh-command claim.
