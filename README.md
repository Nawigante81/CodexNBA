# CodexNBA

Basic working scaffold for the CodexNBA 2025/26 analytics and betting guide with Bulls-focused detail.

## Quick start

1. Install backend dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
2. Run the API + static frontend:
   ```bash
   uvicorn backend.app.main:app --reload
   ```
3. Open http://127.0.0.1:8000/frontend/index.html to interact with the demo UI (teams, Bulls players, prompt outputs, odds upload).

## Endpoints

- `GET /health` – service status.
- `GET /api/teams` – focus teams list.
- `GET /api/bulls/players` – Bulls player snapshots with rotation and injury notes.
- `GET /api/prompts/{id}` – sample outputs for prompts 1–3.
- `POST /api/odds/upload` – upload odds screenshots (saved to `uploads/`).

## Testing

```bash
pytest
```
