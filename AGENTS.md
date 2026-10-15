# Codex development instructions — WordWorld

WordWorld is a student-friendly **NLP course project**. Keep the demo visual, responsive, and easy to run on Windows, while maintaining a clear, inspectable NLP pipeline. Review `README.md` before making architectural changes.

## Structure

- `backend/parser.py`: deterministic natural-language-to-action grammar with optional spaCy tagging
- `backend/main.py`: FastAPI `/api/parse` and `/api/health`
- `frontend/src/Scene.jsx`: custom SVG sprites and interactive scene canvas
- `frontend/src/world.js`: scene objects, spatial placement, actions
- `frontend/src/App.jsx`: React interface, local history, command journal, panels
- `frontend/src/styles.css`: visual design and responsive layout
- `tests/`: NLP tests and evaluation

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

1. Add a front-end integration/smoke test with Playwright after installing packages.
2. Make parser spans and dependencies available as a rich inline explanation.
3. Support sentences like "put a bridge between two houses" with explicit two-target extraction.
