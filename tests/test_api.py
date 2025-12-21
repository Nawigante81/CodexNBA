from io import BytesIO
from pathlib import Path

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


def test_prompt_lookup_invalid_type():
    res = client.get("/api/prompts/not-a-number")
    assert res.status_code == 422


def test_prompt_lookup_out_of_range():
    res = client.get("/api/prompts/0")
    assert res.status_code == 404


def test_upload_odds_screenshot_accepts_image(tmp_path: Path):
    temp_file = tmp_path / "odds.png"
    temp_file.write_bytes(b"fake png data")
    with temp_file.open("rb") as file_handle:
        res = client.post(
            "/api/odds/upload",
            files={"files": ("odds.png", file_handle, "image/png")},
        )
    assert res.status_code == 200
    body = res.json()
    assert body["message"] == "Files saved"
    saved_file = Path(body["files"][0]["path"])
    assert saved_file.exists()
    saved_file.unlink()


def test_upload_odds_screenshot_rejects_non_image():
    res = client.post(
        "/api/odds/upload",
        files={"files": ("odds.txt", BytesIO(b"not an image"), "text/plain")},
    )
    assert res.status_code == 400
    assert res.json()["detail"] == "Only image uploads are supported for odds screenshots"
