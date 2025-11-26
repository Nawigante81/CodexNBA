# CodexNBA



## Quick start

1. Install backend dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
2. Run the API + static frontend:
   ```bash
   uvicorn backend.app.main:app --reload
   ```


## Endpoints

- `GET /health` – service status.
- `GET /api/teams` – focus teams list.
- `GET /api/bulls/players` – Bulls player snapshots with rotation and injury notes.

## Testing

```bash
pytest
```
