# WordWorld initial local verification — 15 October 2026

This records the initial setup run. The latest priority-fix verification is in `evaluation/priority_fixes_report.md`: 142 Python tests, 13 scene tests, 14 browser tests and the production build pass; the original diagnostic-set retest is 46/50, and the second fresh diagnostic set is 40/50.

The reference/coordination round is in `evaluation/reference_fixes_report.md`: 170 Python tests, 16 scene tests, 16 browser tests and the production build pass. Both earlier diagnostic sets retest at 50/50 and 46/50; the third fresh set scores 41/50.

The post-noun/coordination round is in `evaluation/postnoun_fixes_report.md`: **223 Python tests (53 added), 16 scene tests, 18 desktop/mobile browser tests, and the production build passed**. All three saved diagnostic sets retested at **50/50, 47/50 and 45/50**. The fourth fresh 50 scored **40/50 (80%)**, split into 40/40 core cases and 0/10 broader probes.

The quantity/roof/ellipsis round is in `evaluation/ellipsis_fixes_report.md`: 280 Python tests, 16 scene tests, 20 browser tests and the production build passed. The four saved sets retested at 50/50, 47/50, 45/50 and 46/50; the fifth fresh set scored 41/50.

The latest counted-partition/passive/predicate round is in `evaluation/partition_fixes_report.md`: **322 Python tests (42 added), 16 scene tests, 22 desktop/mobile browser tests, and the production build pass**. The five saved sets retest at **50/50, 47/50, 45/50, 46/50 and 46/50**; the sixth fresh 50 scores **41/50 (82%)**, split into 40/40 core cases and 1/10 broader probes. Labels and source hashes were frozen before prediction, with no subsequent parser/gold tuning. These are implementation-aware diagnostic samples. Earlier reports below are historical snapshots.

Dependencies installed into `.venv` and `frontend/node_modules`, including the spaCy `en_core_web_sm` model and Playwright Chromium. The npm lockfile records the frontend dependency resolution.

| Check | Result |
|---|---|
| `python -m pytest -q tests` | 78 passed |
| `python -m tests.evaluate` | 50/50 full-action exact matches |
| `npm test` | 13 scene/preview tests passed |
| `npm run test:e2e` | 12 tests passed across desktop and mobile Chromium |
| `npm run build` | React/Vite production build passed |
| `/api/health` | `ok: true`, `parser: spacy` |
| Vite `/api/parse` proxy | Command returned actions, exact spans, POS/dependency tags and heads |

The same 50 hand-written development commands were run against a saved copy of the original parser and the updated parser:

| Per-command metric | Original | Updated |
|---|---:|---:|
| Intent sequence | 37/50 | 50/50 |
| Entities, counts, colors and setting values | 30/50 | 50/50 |
| Spatial relations and both landmarks, on spatial examples | 10/15 | 15/15 |
| Complete action JSON exact match | 26/50 | 50/50 |

These are development regression results, not held-out or unseen-language accuracy. Both parsers were evaluated on the same expected actions, including the new two-target contract. An independent student-written evaluation set is still needed for a course accuracy claim.

Browser checks verify command submission → Vite proxy → FastAPI → action JSON → SVG object counts and midpoint coordinates. They also verify dragging, keyboard movement, recoloring, duplication/deletion, zoom, undo/redo, autosave, weather clearing, missing-landmark notices, API rejection behavior and restricted offline preview. No page errors occurred in the captured command flow. Desktop and mobile screenshots are saved under `.runtime/wordworld-desktop.png` and `.runtime/wordworld-mobile.png`.

FastAPI is running at http://127.0.0.1:8000 and Vite at http://127.0.0.1:5173. Background process identifiers and startup logs are under `.runtime/`. The in-app browser is open to the app. These processes are local to this machine and must remain running while using it.

Action grounding remains deterministic and rule based. spaCy provides linguistic annotations. Pronoun resolution, color/name filtering of landmarks, spatially filtered removal and guaranteed collision-free dense scenes remain limitations.
