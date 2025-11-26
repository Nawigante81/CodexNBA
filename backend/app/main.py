import asyncio
from pathlib import Path
from typing import List

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.app.services.pipeline import build_pipeline
from data.sample_data import BULLS_PLAYERS, FOCUS_TEAMS

UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="CodexNBA Analytics API", version="0.2.0")

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

pipeline = build_pipeline()
scheduler = AsyncIOScheduler()
scheduler.add_job(pipeline.refresh, "interval", minutes=60, next_run_time=None)


@app.on_event("startup")
async def startup_event():
    await pipeline.refresh()
    scheduler.start()


@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()


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
    payload = pipeline.prompt_payloads().get(key)
    if not payload:
        return JSONResponse(status_code=404, content={"error": "Prompt output not found"})
    return payload


@app.post("/api/odds/upload")
async def upload_odds_screenshot(files: List[UploadFile] = File(...)):
    saved_files = []
    for upload in files:
        safe_name = Path(upload.filename).name
        if not safe_name:
            raise HTTPException(status_code=400, detail="Invalid filename")
        destination = (UPLOAD_DIR / safe_name).resolve()

        if not destination.is_relative_to(UPLOAD_DIR):
            raise HTTPException(status_code=400, detail="Invalid filename")

        destination.write_bytes(await upload.read())
        saved_files.append({"filename": safe_name, "path": str(destination)})
    return {"message": "Files saved", "files": saved_files}


@app.post("/api/refresh")
async def refresh_data():
    state = await pipeline.refresh()
    return {"message": "Pipeline refreshed", "last_run": state.get("last_run"), "sources": state.get("sources")}


@app.get("/api/ingestion/status")
async def ingestion_status():
    return pipeline.get_status()


@app.get("/api/analytics/summary")
async def analytics_summary():
    return pipeline.get_analysis()


@app.get("/")
async def root():
    return {"message": "CodexNBA backend running. Visit /frontend/index.html for demo UI."}
