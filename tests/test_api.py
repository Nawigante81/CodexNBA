from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_focus_teams():
    res = client.get("/api/teams")
    assert res.status_code == 200
    body = res.json()
    assert "focus_teams" in body
    assert "Bulls" in body["focus_teams"]


def test_prompt_lookup_success():
    res = client.get("/api/prompts/1")
    assert res.status_code == 200
    assert "results_vs_closing" in res.json()


def test_prompt_lookup_missing():
    res = client.get("/api/prompts/99")
    assert res.status_code == 404


def test_ingestion_status_and_summary():
    status = client.get("/api/ingestion/status")
    assert status.status_code == 200
    assert "allow_network" in status.json()

    summary = client.get("/api/analytics/summary")
    assert summary.status_code == 200
    payload = summary.json()
    assert "closing_lines" in payload
    assert "prompt_outputs" in payload


def test_manual_refresh():
    res = client.post("/api/refresh")
    assert res.status_code == 200
    assert "last_run" in res.json()
