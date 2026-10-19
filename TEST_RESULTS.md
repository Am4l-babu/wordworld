# WordWorld initial local verification — 15 October 2026

The latest robustness-and-typos round fuzzed the parser, the HTTP API, the scene logic and the frontend with adversarial input; **775 Python tests (3 tracked expected failures), 39 scene tests, 76 desktop/mobile browser checks and the production build pass**, and the same 70-check browser suite passed against the deployed site. Bugs found and fixed: numbers with thousands separators were split into two quantities (`Plant 12,345 trees` built two groups); a 1,200-character list took ~4.7 s to parse (now refused above 40 list separators, worst adversarial case 0.11 s); lone UTF-16 surrogates in a JSON body returned a bare-text 500 that the app mistook for “API offline”; the scene accepted invalid settings, left placement guides pointing at removed landmarks, and placed objects outside the island; imported or shared objects could sit outside the draggable area; edits of a zero count were not skipped. A “Did you mean…?” suggester now recovers typos: on seeded synthetic typos over all 650 labelled commands, the untouched seed recovers **478 of 480** affected commands with 0 wrong fixes and 0 false suggestions on 541 already-correct commands ([report](evaluation/reports/typo_robustness_report.md)). These are implementation-aware diagnostics; earlier entries are historical snapshots.

The latest place-filter round is in [evaluation/reports/filters_fixes_report.md](evaluation/reports/filters_fixes_report.md): **704 Python tests (3 tracked expected failures), 35 scene tests, 70 desktop/mobile browser checks and the production build pass**. The twelfth fresh 50 (place-filtered edits and removals, fractions, new "each"/collection wordings) scored **41/50 (82%) on first run, 39/40 core and 2/10 broader probes**; the one core miss is a labelling error (the gold asked for 18 flowers, above the documented 16-per-action cap) and is kept as a miss. The first run exposed two silent misparses, now fixed and guarded by a notice for unused colors; after fixes the set scores 46/50 and earlier sets are unchanged or better (v7 +1, v8 +1, v9 +1, v10 +2, each checked against gold). The dependency baseline scores 22% on 650 labelled commands against 94% for the rules ([comparison](evaluation/reports/extractor_comparison_report.md)). These are implementation-aware diagnostics; earlier entries are historical snapshots.

The latest edits/references/fractions round is in [evaluation/reports/edits_fixes_report.md](evaluation/reports/edits_fixes_report.md): **627 Python tests, 27 scene tests, 68 desktop/mobile browser checks and the production build pass**, and CI runs the same checks on every pull request. The eleventh fresh 50 (edits, cross-request references with client context, thirds/fifths/percentages) scored **44/50 (88%) on first run, 40/40 core and 4/10 broader probes**, then 50/50 after fixes; every earlier saved set retests unchanged except fresh v10 (40 → 42, fraction fixes). A dependency-parse baseline, frozen before its first run, scores 23% exact on 600 labelled commands against 93% for the rules ([comparison](evaluation/reports/extractor_comparison_report.md)). These are implementation-aware diagnostics; earlier entries are historical snapshots.

The latest quarter/of-each-color/mixed-location/future-perfect round is in [evaluation/reports/quarter_fixes_report.md](evaluation/reports/quarter_fixes_report.md): **525 Python tests (58 grammar cases and one evaluator regression added), 16 scene tests, 44 desktop/mobile browser checks and the production build pass**. Nine saved sets retest at **50/50, 48/50, 45/50, 46/50, 47/50, 46/50, 45/50, 44/50 and 44/50**, with no regressions. The tenth fresh 50 scores **40/50 (80%)**, split into 40/40 core and 0/10 broader probes. Backend and gold hashes preceded first prediction; no subsequent parser/gold tuning occurred. A console-only empty-metric formatting failure was fixed after first predictions were saved, and a separate retry matched the original output exactly. These are implementation-aware diagnostics; earlier entries are historical snapshots.

The latest storm/half/shared-location/future-passive and mobile round is in [evaluation/reports/shared_fixes_report.md](evaluation/reports/shared_fixes_report.md): **466 Python tests (44 added), 16 scene tests, 42 desktop/mobile browser checks and the production build pass**. Eight saved sets retest at **50/50, 48/50, 45/50, 46/50, 47/50, 46/50, 45/50 and 44/50**, with no regressions. The ninth fresh 50 scores **40/50 (80%)**, split into 40/40 core and 0/10 broader probes. Labels and backend fingerprints preceded first prediction; no subsequent parser/gold tuning occurred. These are implementation-aware diagnostics. [Mobile QA](docs/MOBILE_QA.md) includes screenshots and limits. Earlier entries are historical snapshots.

The latest weather/each/inferred-remainder/passive-adverb round is in [evaluation/reports/distributive_fixes_report.md](evaluation/reports/distributive_fixes_report.md): **422 Python tests (62 added), 16 scene tests, 28 desktop/mobile browser tests and the production build pass**. Seven saved sets retest at **50/50, 48/50, 45/50, 46/50, 47/50, 45/50 and 44/50**, with no regressions. The eighth fresh 50 scores **40/50 (80%)**, split into 40/40 core and 0/10 broader probes. Labels and backend hashes were frozen before prediction, with no subsequent parser/gold tuning. These are implementation-aware diagnostics; earlier entries below are historical snapshots.

The latest colon/total-of/remainder round is in [evaluation/reports/colon_fixes_report.md](evaluation/reports/colon_fixes_report.md): **360 Python tests (38 added), 16 scene tests, 26 desktop/mobile browser tests and the production build pass**. Six preserved sets retest at **50/50, 47/50, 45/50, 46/50, 46/50 and 44/50**, with no regressions. The seventh fresh 50 scores **40/50 (80%)**, split into 40/40 core and 0/10 broader probes. All gold actions and backend hashes were frozen before prediction; no subsequent parser/gold tuning occurred. These are implementation-aware diagnostic samples. The README now includes a real animated preview and safe command links into the Vercel app. Earlier entries below are historical snapshots.

This records the initial setup run. The latest priority-fix verification is in `evaluation/reports/priority_fixes_report.md`: 142 Python tests, 13 scene tests, 14 browser tests and the production build pass; the original diagnostic-set retest is 46/50, and the second fresh diagnostic set is 40/50.

The reference/coordination round is in `evaluation/reports/reference_fixes_report.md`: 170 Python tests, 16 scene tests, 16 browser tests and the production build pass. Both earlier diagnostic sets retest at 50/50 and 46/50; the third fresh set scores 41/50.

The post-noun/coordination round is in `evaluation/reports/postnoun_fixes_report.md`: **223 Python tests (53 added), 16 scene tests, 18 desktop/mobile browser tests, and the production build passed**. All three saved diagnostic sets retested at **50/50, 47/50 and 45/50**. The fourth fresh 50 scored **40/50 (80%)**, split into 40/40 core cases and 0/10 broader probes.

The quantity/roof/ellipsis round is in `evaluation/reports/ellipsis_fixes_report.md`: 280 Python tests, 16 scene tests, 20 browser tests and the production build passed. The four saved sets retested at 50/50, 47/50, 45/50 and 46/50; the fifth fresh set scored 41/50.

The latest counted-partition/passive/predicate round is in `evaluation/reports/partition_fixes_report.md`: **322 Python tests (42 added), 16 scene tests, 22 desktop/mobile browser tests, and the production build pass**. The five saved sets retest at **50/50, 47/50, 45/50, 46/50 and 46/50**; the sixth fresh 50 scores **41/50 (82%)**, split into 40/40 core cases and 1/10 broader probes. Labels and source hashes were frozen before prediction, with no subsequent parser/gold tuning. These are implementation-aware diagnostic samples. Earlier reports below are historical snapshots.

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
