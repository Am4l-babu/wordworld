# Codex development instructions — WordWorld

WordWorld is a student-friendly **NLP course project**. Keep the demo visual, responsive, and easy to run on Windows, while maintaining a clear, inspectable NLP pipeline. Review `README.md` before making architectural changes.

## Structure

- `backend/parser.py`: deterministic natural-language-to-action grammar with optional spaCy tagging
- `backend/lexicon.py`, `backend/phrases.py`: vocabulary/regex constants and noun-phrase readers used by the parser
- `backend/edits.py`: recolor/resize/move edits of existing objects; `parse(text, context)` resolves 'it'/'them' against the client's last-touched objects
- `backend/dependency_baseline.py`: comparison-only extractor from spaCy dependencies; frozen (hash in `tests/compare_extractors.py`) — version it rather than tuning it on the labelled sets
- `backend/main.py`: FastAPI `/api/parse` and `/api/health`
- `frontend/src/Scene.jsx`: custom SVG sprites and interactive scene canvas
- `frontend/src/world.js`: scene objects, spatial placement, actions
- `frontend/src/App.jsx`: scene state, undo history, command submission, shortcuts
- `frontend/src/components/`: topbar, journal, composer, explorer, dialogs, dependency arcs
- `frontend/src/share.js`, `view.js`, `theme.js`, `grammar.js`: share links, zoom/pan camera, theme, dependency glossary
- `frontend/src/styles.css`: visual design, responsive layout and light/dark color tokens (`--bg-*`, `--fg-*`, `--line-*`)
- `tests/`: NLP tests and evaluation; `evaluation/`: frozen reports, results and report scripts (see its README)

## Coding goals

- Preserve natural language grounding: every new type/relation must be parsed and be connected to a visible world action.
- Prefer clear, testable rules over ungrounded AI output; add examples and tests for new grammar behavior.
- Never claim spaCy action parsing when only the token annotations come from spaCy. The world is driven by rule-based grounding; the dependency baseline is labelled as a comparison and never applied.
- Keep object manipulations working (click, drag, add, remove, recolor, undo, zoom).
- Maintain responsive design and keyboard accessibility wherever practical.
- Run Python tests and `npm run build` before considering a change complete. If installing dependencies fails due to network, report that limitation rather than claiming the build succeeded.

## Useful development commands

Backend: `python -m uvicorn backend.main:app --reload --port 8000`
Frontend: `cd frontend && npm install && npm run dev`
Tests: `python -m pytest -q tests && python -m tests.evaluate && python -m tests.compare_extractors --check`; frontend `npm test`, `npm run build`, `npm run test:e2e` (CI runs all)

## Highest-priority next tasks

Done: Playwright desktop/mobile suite, inline dependency-arc explanation, two-target `between` extraction, language edits, cross-request references, CI, rules-vs-dependency comparison, thirds/fifths/percentages, pinch-to-zoom, frozen round-eleven set (`tests/fresh_commands_v11.json`).

1. Remaining grammar gaps: alternate "each" wording and cross-clause collections (see `evaluation/reports/quarter_fixes_report.md`).
2. Spatially filtered edits and removals ("paint the trees near the lake red") need a filter field in the action schema and the scene.
3. Freeze a round-twelve set before tuning on any new grammar; keep first-run and retest numbers separate.
