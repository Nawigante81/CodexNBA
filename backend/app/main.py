from pathlib import Path
from typing import List

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from data.sample_data import BULLS_PLAYERS, FOCUS_TEAMS, PROMPT_OUTPUTS

UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="CodexNBA Analytics API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/frontend",
    StaticFiles(directory=Path(__file__).resolve().parents[2] / "frontend"),
    name="frontend",
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/teams")
async def list_focus_teams():
    return {"focus_teams": FOCUS_TEAMS}


@app.get("/api/bulls/players")
async def bulls_players():
    return {"players": BULLS_PLAYERS}


@app.get("/api/prompts/{prompt_id}")
async def prompt_output(prompt_id: str):
    key = f"prompt_{prompt_id}"
    payload = PROMPT_OUTPUTS.get(key)
    if not payload:
        return JSONResponse(status_code=404, content={"error": "Prompt output not found"})
    return payload


@app.post("/api/odds/upload")
async def upload_odds_screenshot(files: List[UploadFile] = File(...)):
    saved_files = []
    for upload in files:
        destination = UPLOAD_DIR / upload.filename
        destination.write_bytes(await upload.read())
        saved_files.append({"filename": upload.filename, "path": str(destination)})
    return {"message": "Files saved", "files": saved_files}


@app.get("/")
async def root():
    return {"message": "CodexNBA backend running. Visit /frontend/index.html for demo UI."}
