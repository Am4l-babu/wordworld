"""WordWorld NLP API. Run: uvicorn backend.main:app --reload"""
import json
from pathlib import Path
from typing import Literal
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from . import parser
from .dependency_baseline import extract_text
from .lexicon import ALIASES
from .parser import parse, NLP_STATUS, SCENE_LIMIT

app = FastAPI(title="WordWorld NLP API", version="1.0.0", description="Interpret free-form natural language as structured world-building actions.")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["*"])

ObjectType = Literal[tuple(ALIASES)]


class FocusGroup(BaseModel):
    type: ObjectType
    count: int = Field(ge=1, le=SCENE_LIMIT)


class Prompt(BaseModel):
    text: str = Field(min_length=1, max_length=1400)
    # What the previous command touched, so "make it blue" can follow "build a castle".
    context: list[FocusGroup] = Field(default_factory=list, max_length=12)

@app.get("/api/health")
def health():
    return {"ok": True, "parser": NLP_STATUS}

@app.post("/api/parse")
def parse_prompt(prompt: Prompt):
    try:
        result = parse(prompt.text, [group.model_dump() for group in prompt.context])
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    # Comparison only: the world applies `actions`; `baseline` is what dependency arcs alone would extract.
    # A failure in the comparison must never cost the person their real result.
    try:
        result["baseline"] = extract_text(parser.NLP, prompt.text)
    except Exception:  # noqa: BLE001 - comparison is best-effort
        result["baseline"] = None
    return result


SCORES = Path(__file__).with_name("extractor_scores.json")


@app.get("/api/extractors")
def extractor_scores():
    """Corpus-level rules vs dependency-baseline scores from tests/compare_extractors.py."""
    if not SCORES.is_file():
        raise HTTPException(status_code=404, detail="Run python -m tests.compare_extractors to create the comparison.")
    return json.loads(SCORES.read_text(encoding="utf-8"))

# Optional: serve compiled React UI after `npm run build`.
dist = Path(__file__).resolve().parents[1] / "frontend" / "dist"
if dist.is_dir():
    app.mount("/assets", StaticFiles(directory=dist / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def frontend(full_path: str):
        if full_path == "api" or full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Unknown API route.")
        target = (dist / full_path).resolve()
        if target.is_file() and dist in target.parents:
            return FileResponse(target)
        return FileResponse(dist / "index.html")
