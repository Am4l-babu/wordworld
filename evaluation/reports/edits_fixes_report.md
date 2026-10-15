# Round eleven: language edits, cross-request references and fractions

This round adds edits of existing objects (recolor, resize, move by landmark or direction), references that carry across requests through client context, and thirds/fifths/tenths/percentages in counted partitions.

## Frozen first run

`tests/fresh_commands_v11.json` (SHA-256 `6c736a5d351b…`) was labelled by `tests/create_fresh_set_v11.py` and frozen before the parser ever ran on it; the backend fingerprint matched at evaluation time. Cases with a `context` field pass it to the parser exactly as the browser would.

| Metric | First run |
|---|---|
| exact match | 44/50 |
| intent | 45/50 |
| entity count color | 45/50 |
| spatial | 10/11 |
| settings | 1/1 |
| core cases | 40/40 |
| broader probes | 4/10 |

All 40 core cases were exact on first sight; 6 of 10 broader probes failed:

- **R41** “Turn the two blue houses white.” — expected `[{"action": "recolor", "type": "house", "count": 2, "color": "white", "filter_color": "blue"}]`, got `[]` (explicit_abstention)
- **R42** “Give the cottage a red roof.” — expected `[{"action": "recolor", "type": "house", "count": 1, "color": "red"}]`, got `[]` (explicit_abstention)
- **R43** “Move the castle closer to the lake.” — expected `[{"action": "move", "type": "castle", "count": 1, "relation": "near", "target": "lake"}]`, got `[]` (explicit_abstention)
- **R44** “Make both houses green.” — expected `[{"action": "recolor", "type": "house", "count": 2, "color": "green"}]`, got `[{"action": "add", "type": "house", "count": 1, "color": "green"}]` (wrong_fields)
- **R45** “Make the houses a bit taller.” — expected `[{"action": "resize", "type": "house", "count": "all", "scale": 1.12}]`, got `[{"action": "add", "type": "house", "count": 1, "color": null}]` (wrong_fields)
- **R46** “Move the castle up a little.” — expected `[{"action": "move", "type": "castle", "count": 1, "direction": "up", "distance": "small"}]`, got `[{"action": "move", "type": "castle", "count": 1, "direction": "up", "distance": "medium"}]` (wrong_fields)

Two of these were wrong actions rather than abstentions: “make both houses green” and “make the houses a bit taller” created a house. Both now edit existing houses.

## Fixes after the first run

- `both` and `the two …` name existing objects; `taller`, `shorter`, `wider` resize
- `closer to` is a `near` relation; an amount may follow a direction (`up a little`) or precede a place (`a little closer to the house`)
- `give the cottage a red roof` recolors the part a sprite draws; `give me two houses` still creates

## Retests after the fixes

These retests use sets the parser has now seen, so they are not accuracy estimates. They show that no earlier set regressed.

| Set | Round ten | After round-eleven fixes |
|---|---|---|
| heldout | 50/50 | 50/50 |
| fresh_v2 | 48/50 | 48/50 |
| fresh_v3 | 45/50 | 45/50 |
| fresh_v4 | 46/50 | 46/50 |
| fresh_v5 | 47/50 | 47/50 |
| fresh_v6 | 46/50 | 46/50 |
| fresh_v7 | 45/50 | 45/50 |
| fresh_v8 | 44/50 | 44/50 |
| fresh_v9 | 44/50 | 44/50 |
| fresh_v10 | 40/50 | 42/50 |
| fresh_v11 | — (first run 44/50) | 50/50 |

The two fresh-v10 gains are the fraction fixes (`one third purple and two thirds green`, `25% pink and 75% purple`).

These are implementation-aware, hand-authored diagnostics, not independent accuracy estimates.
