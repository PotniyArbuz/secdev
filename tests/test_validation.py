from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
headers = {"Authorization": "Bearer fake-token"}


def test_extra_field_rejected():
    payload = {"title": "Run", "periodicity": "daily", "malicious": "x"}
    resp = client.post("/habits", json=payload, headers=headers)
    assert resp.status_code == 422
    detail = resp.json()["detail"]
    assert any("extra" in err["msg"].lower() for err in detail)


def test_invalid_periodicity():
    payload = {"title": "Run", "periodicity": "monthly"}
    resp = client.post("/habits", json=payload, headers=headers)
    assert resp.status_code == 422
    detail = resp.json()["detail"]
    assert any("Input should be 'daily' or weekly" in err["msg"] for err in detail)


def test_utc_normalization():
    r = client.post("/habits", json={"title": "Sleep", "periodicity": "daily"}, headers=headers)
    hid = r.json()["id"]
    dt = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    resp = client.post(f"/habits/{hid}/checkins", json={"date": dt.isoformat()}, headers=headers)
    assert resp.status_code == 200
    checkin_date = resp.json()["date"]
    assert checkin_date.startswith("2025-01-01T12:00:00")
