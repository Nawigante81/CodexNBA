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

## Co jeszcze potrzebne do pełnego działania (PRO)

- **Prawdziwe zasilanie danych:** harmonogram/worker z trwałym storage (np. Postgres/Redis) do zbierania pełnych game logs, box score'ów, terminarzy i linii closing/opening z wielu sportsbooków (Bet365, Pinnacle, William Hill) zamiast sampli HTML. 
- **Obsługa uploadów kursów:** parser OCR/hand-off, który po wgraniu zrzutów mapuje linie/numery rynku do parlay generatora, oraz walidacja czasu/źródła. 
- **Injury i news ingest:** aggegacja z NBA.com, feedów beat-writerów/major news, cache + deduplikacja oraz alerty na zmiany statusu (O/Q/D/OUT) w oknie meczowym. 
- **Analiza zgodna ze specyfikacją:** realne modele tempa/off-def ratingu, head-to-head, travel/rest, formy graczy (rolling 5–10 gier) oraz porównanie do linii closing + generowanie propsów (w tym Bulls parlay) na bazie aktualnych kursów. 
- **Frontend produkcyjny:** UI z filtrowaniem po drużynie/dacie, widokami promptów 1–3, oraz checklistą kontuzji/ryzyk; pobieranie danych z API zamiast statycznych sampli. 
- **Bezpieczeństwo i operacje:** logowanie/monitoring, rate limiting, obsługa błędów sieci, retry + backoff, healthchecks schedulerów oraz konfiguracja środowiskowa (sekrety, API keys) w zmiennych `.env`. 
- **Testy/CI:** pokrycie e2e (ingest → analiza → API), kontrakty parserów HTML/OCR, oraz pipeline smoke testy w trybie offline/online w CI.
