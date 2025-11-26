# CodexNBA

Working scaffold for the CodexNBA 2025/26 analytics and betting guide with Bulls-focused detail, live ingest, and scheduled refresh.

## Quick start

1. Install backend dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
2. Run the API + static frontend:
   ```bash
   uvicorn backend.app.main:app --reload
   ```
3. Open http://127.0.0.1:8000/frontend/index.html to interact with the demo UI (ingestion status, analytics summary, teams, Bulls players, prompt outputs, odds upload).

## Endpoints

- `GET /health` – service status.
- `GET /api/teams` – focus teams list.
- `GET /api/bulls/players` – Bulls player snapshots with rotation and injury notes.
- `GET /api/prompts/{id}` – prompt-ready outputs derived from ingest cache.
- `GET /api/ingestion/status` – last run + per-source status, including network/offline mode.
- `POST /api/refresh` – manual refresh of Basketball-Reference, VegasInsider, and NBA injury feeds.
- `GET /api/analytics/summary` – analytics bundle (pace flags, injury flags, prompt outputs, Bulls form).
- `POST /api/odds/upload` – upload odds screenshots (saved to `uploads/`).

## Scheduler + ingestion

- An AsyncIO scheduler runs hourly to refresh Basketball-Reference box scores, VegasInsider closing lines, and NBA injury data.
- Set `PIPELINE_OFFLINE=1` to force offline mode (uses bundled sample data without network).
- Cache is written to `data/pipeline_cache.json` after each refresh.

## Testing

```bash
pytest
```
