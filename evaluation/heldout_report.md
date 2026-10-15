# WordWorld: 50 new commands — 15 October 2026

**Result: 35/50 complete action matches (70.0%). The parser was not modified.**

This is a new hand-authored diagnostic challenge set, frozen with expected action JSON before its first parser execution. All 50 commands are unique and have no normalized exact matches in the existing development JSON, Python test literals, browser smoke test literals, or README command lines. Similar grammatical constructions are intentionally represented; lexical/structural independence is not claimed.

The author had already seen the implementation and development examples. This is not an independently human-labeled or randomly sampled benchmark, so 70% should not be presented as population/user-traffic accuracy. The six capability probes are identified in advance; some deliberately test documented limitations, notably pronouns. No gold labels or parser rules were tuned after observing predictions.

## Accuracy

| Metric | Correct / total | Accuracy |
|---|---:|---:|
| Complete ordered action JSON | 35/50 | 70.0% |
| Action-name sequence | 39/50 | 78.0% |
| Object/action/count/color sequence, over all commands | 36/50 | 72.0% |
| Spatial fields on commands with a gold relation | 18/22 | 81.8% |
| Time/weather values on commands with gold settings | 5/6 | 83.3% |

Exact match requires every ordered action dictionary to match, including quantities, colors, relation targets and setting values. Field metrics are per-command sequence comparisons, not per-token accuracy. The all-command object metric includes matching empty object lists in pure-setting and intentional no-op cases. Spatial/setting metrics use their gold-bearing subsets and do not measure overall command correctness.

| Preassigned scope | Exact matches | Accuracy |
|---|---:|---:|
| Core commands | 35/44 | 79.5% |
| Capability probes | 0/6 | 0.0% |

There were **15 errors and no parser exceptions**. Twelve incorrect commands had no parser warning; the three pronoun failures did emit a notice. Landmarks were assumed to exist, and parsing was evaluated independently for each command. Scene geometry, whether a material color is rendered, and conversation history across requests were not scored.

## Main remaining errors and fixes

| Priority | Error pattern | Failed cases | Observed example | Suggested fix |
|---|---|---|---|---|
| 1 | Negation variants | H48, H49 | `Don’t add any bridges.` creates a bridge; `Make it not rain.` emits no action instead of clear weather. | Normalize Unicode apostrophes before matching (preserving original-span offsets), and interpret negation at the intent/setting level. |
| 2 | Front-loaded location phrases | H33–H35 | `Near the lake, plant four trees.` creates an extra lake and loses the near relation. | Attach an initial prepositional phrase to the following action; classify its nouns as landmarks before clause splitting. |
| 2 | Protected/context-only nouns | H43, H44 | `Keep the houses and remove the trees.` adds a house; `Leave the lake alone and add a bridge.` adds a lake. | Recognize preservation/context clauses; only action subjects should become creations. Avoid fallback creation for every recognized noun. |
| 3 | Quantity vocabulary | H26–H29 | Eleven houses, a dozen flowers, a pair of rocks, and twelve cottages all become count 1. | Expand cardinal and quantifier phrases within the 16-object cap; warn rather than silently default on unrecognized quantities. |
| 4 | Pronoun resolution | H30–H32 | `Build a house, then remove it.` only builds the house. | Track typed referents through actions within one utterance; use explicit ambiguity handling before extending to cross-request history. |
| 5 | Elliptical coordination | H38 | `Build one red and one blue house.` produces only one blue house. | Expand coordinated modifier phrases into distinct noun phrases/actions while preserving each color and count. |

Basic alias lookup, post-noun relations, and explicit mixed actions performed well on these examples. The failures mostly concern phrase attachment, scope and reference resolution. spaCy is installed and supplies annotations, but current action grounding is lexical/rule based; its dependency parse is not used to resolve these semantics.

## Category breakdown

| Category | Correct / total | Errors |
|---|---:|---:|
| Aliases and familiar noun phrases | 6/6 | 0 |
| Post-noun spatial relations | 9/9 | 0 |
| Multiple actions and modifier scope | 9/9 | 0 |
| Time/weather wording | 4/5 | 1 |
| Negation, zero quantities and contrasts | 7/8 | 1 |
| New quantity expressions | 0/4 | 4 |
| Within-command pronoun reference | 0/3 | 3 |
| Location phrase before the verb | 0/3 | 3 |
| Coordinated colors with an omitted noun | 0/1 | 1 |
| Keep/leave-alone object mentions | 0/2 | 2 |

## All 50 commands

| ID | Scope | Result | Command |
|---|---|---|---|
| H01 | core | PASS | Please build four purple cottages beside the stream. |
| H02 | core | PASS | Plant seven green trees south of the tower. |
| H03 | core | PASS | Place 6 yellow blossoms north of the fortress. |
| H04 | core | PASS | Give me three white cabins west of the pond. |
| H05 | core | PASS | Draw two paths next to the creek. |
| H06 | core | PASS | Put a boulder in the center of the garden. |
| H07 | core | PASS | Show a lighthouse at the back of the cottages. |
| H08 | core | PASS | Create nine pink flowers around the lake. |
| H09 | core | PASS | Insert a mountain to the right of the bridge. |
| H10 | core | PASS | Grow a woodland close to the road. |
| H11 | core | PASS | Add 12 blue homes. |
| H12 | core | PASS | Build a bridge between the tower and the castle. |
| H13 | core | PASS | Place two rocks between the pond and the house. |
| H14 | core | PASS | Plant three flowers within the castle. |
| H15 | core | PASS | Build a hut, a tower, and a road. |
| H16 | core | PASS | Delete 4 boulders, then plant six blossoms. |
| H17 | core | PASS | Cut down a couple of trees; create a pond. |
| H18 | core | PASS | Erase one bridge and place three yellow cottages. |
| H19 | core | PASS | Clear the map; show a river and a bridge. |
| H20 | core | PASS | Make it morning and plant two trees. |
| H21 | core | PASS | Make it midnight with snowing. |
| H22 | core | PASS | Stop the snow and make it sunshine. |
| H23 | core | PASS | Do not erase the towers; plant five trees. |
| H24 | core | PASS | Don't build houses, towers, or castles; add a rock. |
| H25 | core | PASS | Add zero bridges and zero roads. |
| H26 | core | FAIL | Build eleven houses near the lake. |
| H27 | core | FAIL | Plant a dozen flowers behind the tower. |
| H28 | core | FAIL | Place a pair of rocks beside the river. |
| H29 | core | FAIL | Add twelve orange cottages. |
| H30 | capability_probe | FAIL | Build a house, then remove it. |
| H31 | capability_probe | FAIL | Build a red house and a blue house, then put a tree between them. |
| H32 | capability_probe | FAIL | Plant five trees and then delete two of them. |
| H33 | core | FAIL | Near the lake, plant four trees. |
| H34 | core | FAIL | To the left of the castle, build a tower. |
| H35 | core | FAIL | Between the house and the tower, place a bridge. |
| H36 | core | PASS | Add a tree near the lake and a flower beside the castle. |
| H37 | core | PASS | Build three red houses and three blue towers. |
| H38 | capability_probe | FAIL | Build one red and one blue house. |
| H39 | core | PASS | Add three red houses and two blue flowers near the river. |
| H40 | core | PASS | Remove all houses and all towers. |
| H41 | core | PASS | Don't remove any trees, but add two flowers. |
| H42 | core | PASS | Please do not add a tree or a rock. |
| H43 | capability_probe | FAIL | Keep the houses and remove the trees. |
| H44 | capability_probe | FAIL | Leave the lake alone and add a bridge. |
| H45 | core | PASS | Remove no trees and add two rocks. |
| H46 | core | PASS | Build two houses but not a castle. |
| H47 | core | PASS | Make it rain, then stop raining. |
| H48 | core | FAIL | Make it not rain. |
| H49 | core | FAIL | Don’t add any bridges. |
| H50 | core | PASS | Make it snow; clear the world; add a pink house. |

## Expected vs. actual for every failure

### H26: Build eleven houses near the lake.

Category: New quantity expressions. Scope: core. Outcome: wrong_fields.

Expected:

```json
[
  {
    "action": "add",
    "type": "house",
    "count": 11,
    "color": null,
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
    "count": 1,
    "color": null,
    "relation": "near",
    "target": "lake"
  }
]
```

Parser notices: None.

### H27: Plant a dozen flowers behind the tower.

Category: New quantity expressions. Scope: core. Outcome: wrong_fields.

Expected:

```json
[
  {
    "action": "add",
    "type": "flower",
    "count": 12,
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
    "type": "flower",
    "count": 1,
    "color": null,
    "relation": "above",
    "target": "tower"
  }
]
```

Parser notices: None.

### H28: Place a pair of rocks beside the river.

Category: New quantity expressions. Scope: core. Outcome: wrong_fields.

Expected:

```json
[
  {
    "action": "add",
    "type": "rock",
    "count": 2,
    "color": null,
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
    "type": "rock",
    "count": 1,
    "color": null,
    "relation": "near",
    "target": "river"
  }
]
```

Parser notices: None.

### H29: Add twelve orange cottages.

Category: New quantity expressions. Scope: core. Outcome: wrong_fields.

Expected:

```json
[
  {
    "action": "add",
    "type": "house",
    "count": 12,
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
    "color": "orange"
  }
]
```

Parser notices: None.

### H30: Build a house, then remove it.

Category: Within-command pronoun reference. Scope: capability_probe. Outcome: missing_actions.

Label rationale: Within-command antecedent: it refers to the newly created house. Pronoun resolution is a documented limitation.

Expected:

```json
[
  {
    "action": "add",
    "type": "house",
    "count": 1,
    "color": null
  },
  {
    "action": "remove",
    "type": "house",
    "count": 1
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

Parser notices: No supported object or setting found in one clause. Name an object explicitly; pronoun references are not resolved.

### H31: Build a red house and a blue house, then put a tree between them.

Category: Within-command pronoun reference. Scope: capability_probe. Outcome: missing_actions.

Label rationale: Them refers to the two newly created houses. This tests a documented capability gap.

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
    "count": 1,
    "color": "blue"
  },
  {
    "action": "add",
    "type": "tree",
    "count": 1,
    "color": null,
    "relation": "between",
    "target": "house",
    "targets": [
      "house",
      "house"
    ]
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
    "color": "red"
  },
  {
    "action": "add",
    "type": "house",
    "count": 1,
    "color": "blue"
  }
]
```

Parser notices: A spatial instruction needs named landmarks; use 'between two houses' or 'between the house and the lake'.

### H32: Plant five trees and then delete two of them.

Category: Within-command pronoun reference. Scope: capability_probe. Outcome: missing_actions.

Label rationale: Them refers to the five newly created trees; remove two, not all five.

Expected:

```json
[
  {
    "action": "add",
    "type": "tree",
    "count": 5,
    "color": null
  },
  {
    "action": "remove",
    "type": "tree",
    "count": 2
  }
]
```

Actual:

```json
[
  {
    "action": "add",
    "type": "tree",
    "count": 5,
    "color": null
  }
]
```

Parser notices: No supported object or setting found in one clause. Name an object explicitly; pronoun references are not resolved.

### H33: Near the lake, plant four trees.

Category: Location phrase before the verb. Scope: core. Outcome: extra_actions.

Label rationale: Initial prepositional phrase modifies plant; lake is an existing landmark.

Expected:

```json
[
  {
    "action": "add",
    "type": "tree",
    "count": 4,
    "color": null,
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
    "type": "lake",
    "count": 1,
    "color": null
  },
  {
    "action": "add",
    "type": "tree",
    "count": 4,
    "color": null
  }
]
```

Parser notices: None.

### H34: To the left of the castle, build a tower.

Category: Location phrase before the verb. Scope: core. Outcome: extra_actions.

Expected:

```json
[
  {
    "action": "add",
    "type": "tower",
    "count": 1,
    "color": null,
    "relation": "left",
    "target": "castle"
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
  },
  {
    "action": "add",
    "type": "tower",
    "count": 1,
    "color": null
  }
]
```

Parser notices: None.

### H35: Between the house and the tower, place a bridge.

Category: Location phrase before the verb. Scope: core. Outcome: extra_actions.

Expected:

```json
[
  {
    "action": "add",
    "type": "bridge",
    "count": 1,
    "color": null,
    "relation": "between",
    "target": "house",
    "targets": [
      "house",
      "tower"
    ]
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
  },
  {
    "action": "add",
    "type": "tower",
    "count": 1,
    "color": null
  },
  {
    "action": "add",
    "type": "bridge",
    "count": 1,
    "color": null
  }
]
```

Parser notices: None.

### H38: Build one red and one blue house.

Category: Coordinated colors with an omitted noun. Scope: capability_probe. Outcome: missing_actions.

Label rationale: One red [house] and one blue house: the omitted first noun denotes a separate house.

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
    "color": "blue"
  }
]
```

Parser notices: None.

### H43: Keep the houses and remove the trees.

Category: Keep/leave-alone object mentions. Scope: capability_probe. Outcome: extra_actions.

Label rationale: Keep explicitly protects houses. No new action type is needed: emit only tree removal.

Expected:

```json
[
  {
    "action": "remove",
    "type": "tree",
    "count": "all"
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
  },
  {
    "action": "remove",
    "type": "tree",
    "count": "all"
  }
]
```

Parser notices: None.

### H44: Leave the lake alone and add a bridge.

Category: Keep/leave-alone object mentions. Scope: capability_probe. Outcome: extra_actions.

Label rationale: Lake is a protected mention, not an add subject.

Expected:

```json
[
  {
    "action": "add",
    "type": "bridge",
    "count": 1,
    "color": null
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
    "type": "bridge",
    "count": 1,
    "color": null
  }
]
```

Parser notices: None.

### H48: Make it not rain.

Category: Time/weather wording. Scope: core. Outcome: silent_omission.

Label rationale: The weather enum is mutually exclusive; requesting non-rain maps to clear in this evaluation.

Expected:

```json
[
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

Parser notices: None.

### H49: Don’t add any bridges.

Category: Negation, zero quantities and contrasts. Scope: core. Outcome: unrequested_actions.

Label rationale: U+2019 apostrophe; same negation meaning as ASCII Don't.

Expected:

```json
[]
```

Actual:

```json
[
  {
    "action": "add",
    "type": "bridge",
    "count": 1,
    "color": null
  }
]
```

Parser notices: None.

## Reproducibility and integrity

From the project root, with the installed environment:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m tests.evaluate_heldout
.\.venv\Scripts\python.exe -X utf8 evaluation\write_heldout_report.py
```

The runner refuses changed gold labels or a parser whose source differs from the baseline captured before evaluation. Expected language errors remain in the result JSON; the script completes successfully when the evaluation itself ran. It does not silently rewrite the gold set or add these examples to the development tests.

- Dataset: `tests/heldout_commands.json`
- Full predictions and notices: `evaluation/heldout_results.json`
- Prediction-free dataset construction: `tests/create_heldout_set.py`
- Runner: `tests/evaluate_heldout.py`

- Frozen dataset SHA256: `d372d2d85208319439929068902779ba4ea9144722caea783a8c792bcbd7a224`
- Parser SHA256 before: `ae2df7bbad16d5b8f9973154c7ef4b70b1fbab9a9ac27e9d047c3784a7c7a91a`
- Parser SHA256 after: `ae2df7bbad16d5b8f9973154c7ef4b70b1fbab9a9ac27e9d047c3784a7c7a91a`

Runtime: python=3.12.7, spacy=3.8.16, en_core_web_sm=3.8.0, annotations=spacy, grounding=rules.

Once these failures guide parser changes, this set becomes a regression/comparison set. Author another fresh set for a future unseen-command accuracy claim.
