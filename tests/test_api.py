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

