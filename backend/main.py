"""WordWorld NLP API. Run: uvicorn backend.main:app --reload"""
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from .parser import parse, NLP_STATUS

app = FastAPI(title="WordWorld NLP API", version="1.0.0", description="Interpret free-form natural language as structured world-building actions.")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["*"])

class Prompt(BaseModel):
    text: str = Field(min_length=1, max_length=1400)

@app.get("/api/health")
def health():
    return {"ok": True, "parser": NLP_STATUS}

@app.post("/api/parse")
def parse_prompt(prompt: Prompt):
    try:
        return parse(prompt.text)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

# Optional: serve compiled React UI after `npm run build`.
dist = Path(__file__).resolve().parents[1] / "frontend" / "dist"
if dist.is_dir():
    app.mount("/assets", StaticFiles(directory=dist / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def frontend(full_path: str):
        target = (dist / full_path).resolve()
        if target.is_file() and dist in target.parents:
            return FileResponse(target)
        return FileResponse(dist / "index.html")
