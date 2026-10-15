# Codex development instructions — WordWorld

WordWorld is a student-friendly **NLP course project**. Keep the demo visual, responsive, and easy to run on Windows, while maintaining a clear, inspectable NLP pipeline. Review `README.md` before making architectural changes.

## Structure

- `backend/parser.py`: deterministic natural-language-to-action grammar with optional spaCy tagging
- `backend/lexicon.py`, `backend/phrases.py`: vocabulary/regex constants and noun-phrase readers used by the parser
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
- Never claim spaCy action parsing when only the token annotations come from spaCy. The current MVP uses rule-based grounding.
- Keep object manipulations working (click, drag, add, remove, recolor, undo, zoom).
- Maintain responsive design and keyboard accessibility wherever practical.
- Run Python tests and `npm run build` before considering a change complete. If installing dependencies fails due to network, report that limitation rather than claiming the build succeeded.

## Useful development commands

Backend: `python -m uvicorn backend.main:app --reload --port 8000`
Frontend: `cd frontend && npm install && npm run dev`
Tests: `python -m pytest -q tests && python -m tests.evaluate`

## Highest-priority next tasks

Done: Playwright desktop/mobile suite, inline dependency-arc explanation, two-target `between` extraction.

1. Broader grammar gaps from the latest report: thirds, percentages, alternate "each" wording and cross-clause collections.
2. Cross-request references ("make it blue" after a previous command) without global server state.
3. Touch pinch-to-zoom on the scene (buttons, Ctrl+wheel and drag-to-pan exist today).
