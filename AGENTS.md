# Codex development instructions — WordWorld

WordWorld is a student-friendly **NLP course project**. Keep the demo visual, responsive, and easy to run on Windows, while maintaining a clear, inspectable NLP pipeline. Review `README.md` before making architectural changes.

## Structure

- `backend/parser.py`: deterministic natural-language-to-action grammar with optional spaCy tagging
- `backend/lexicon.py`, `backend/phrases.py`: vocabulary/regex constants and noun-phrase readers used by the parser
- `backend/edits.py`: recolor/resize/move edits of existing objects; `parse(text, context)` resolves 'it'/'them' against the client's last-touched objects
- `backend/suggest.py`: typo suggestions ("Did you mean...?"); vocabulary is read from the grammar's own regexes, a correction must make the parse measurably better, `tests/evaluate_typos.py` measures it on seeded synthetic typos (seed 3 is the untouched headline seed; do not tune on it)
- `frontend/src/testlog.js`, `components/TestLogDialog.jsx`: the local, never-sent user-test log; `tests/analyze_usertests.py` analyses downloaded logs (put them in git-ignored `evaluation/usertests/`; see `docs/USER_TESTING.md`)
- `backend/ratelimit.py`: per-client sliding-window limiter on `POST /api/parse` (default 300/min, `WORDWORLD_RATE_LIMIT`/`WORDWORLD_RATE_WINDOW`, 0 disables; loopback exempt; X-Forwarded-For trusted only on Vercel or with `WORDWORLD_TRUST_PROXY`). Best effort: state is per instance, so use the host's firewall rules for hard limits
- `tests/ablation.py`, `tests/make_figures.py`, `docs/REPORT.md`: component ablation with Wilson intervals, SVG figures drawn from the recorded results, and the project write-up (re-run both scripts after changing the parser)
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
- Maintain responsive design and keyboard accessibility. `frontend/tests/browser/a11y.spec.js` runs axe-core (WCAG 2.2 AA + best practices) in both themes on every reachable state and must stay at zero violations: new text colors need 4.5:1 contrast on their surface, accessible names must contain their visible text, and text must not be faded with `opacity`.
- Run Python tests and `npm run build` before considering a change complete. If installing dependencies fails due to network, report that limitation rather than claiming the build succeeded.

## Useful development commands

Backend: `python -m uvicorn backend.main:app --reload --port 8000`
Frontend: `cd frontend && npm install && npm run dev`
Tests: `python -m pytest -q tests && python -m tests.evaluate && python -m tests.compare_extractors --check` (pytest includes the typo-quality guards); frontend `npm test`, `npm run build`, `npm run test:e2e` (CI runs all)

## Highest-priority next tasks

Done: Playwright desktop/mobile suite, inline dependency-arc explanation, two-target `between` extraction, language edits, cross-request references, CI, rules-vs-dependency comparison, thirds/fifths/percentages, pinch-to-zoom, place filters for edits/removals, frozen round-eleven and round-twelve sets (`tests/fresh_commands_v11.json`, `_v12.json`).

1. Remaining grammar gaps, tracked as strict xfails in `tests/test_filter_fixes.py`: a count after a color list ("in each of pink and white, two per color"), trailing each-counts ("four of each"), group multiplication ("two clusters of three").
2. Place filters cover near/left/right/behind/in front of/inside one named landmark; `between`/`across` filters and pronoun landmarks ("the trees near it") are refused with a notice and need scene support.
3. Freeze a round-thirteen set before tuning on any new grammar; keep first-run and retest numbers separate. Never edit a frozen label, even a wrong one (round twelve's S39): disclose it in the report.
4. Typo handling: human typos (phonetic spellings, missing spaces) are not modelled; ties between equally close words (`towes`: towers/towns) need context.
5. Measure real people: run `docs/USER_TESTING.md` sessions and feed `tests/analyze_usertests.py` output into a new frozen set.
6. Keep fuzzing: `/api/parse` input limits (1,400 chars, 40 list separators), parse time (<1 s on adversarial input) and the scene invariants in `frontend/tests/world.fuzz.test.js` are guarded by tests; extend them when adding grammar.
