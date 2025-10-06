from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def setup_function():
    global _habit_id_counter, _checkin_id_counter
    app.extra["_DB"] = {"habits": [], "checkins": []}
    app.extra["_habit_id_counter"] = 0
    app.extra["_checkin_id_counter"] = 0


def test_create_and_get_habit():
    headers = {"Authorization": "Bearer fake-token"}
    resp = client.post(
        "/habits", json={"name": "Drink water", "periodicity": "daily"}, headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()
    hid = data["id"]

    resp = client.get(f"/habits/{hid}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == hid


def test_list_habits():
    headers = {"Authorization": "Bearer fake-token"}
    resp = client.get("/habits", headers=headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

    client.post("/habits", json={"name": "Run", "periodicity": "daily"}, headers=headers)
    resp = client.get("/habits", headers=headers)
    assert len(resp.json()) > 0


def test_add_and_list_checkin():
    headers = {"Authorization": "Bearer fake-token"}
    r = client.post("/habits", json={"name": "Read", "periodicity": "daily"}, headers=headers)
    assert r.status_code == 200
    hid = r.json()["id"]

    r2 = client.post(
        f"/habits/{hid}/checkins", json={"date": "2025-09-30", "value": "True"}, headers=headers
    )
    assert r2.status_code == 200

    r3 = client.get(f"/habits/{hid}/checkins", headers=headers)
    assert r3.status_code == 200
    assert len(r3.json()) == 1


def test_invalid_periodicity():
    headers = {"Authorization": "Bearer fake-token"}
    resp = client.post("/habits", json={"name": "Run", "periodicity": "invalid"}, headers=headers)
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "validation_error"
    assert "Periodicity must be 'daily' or 'weekly'" in resp.json()["error"]["message"]


def test_stats():
    headers = {"Authorization": "Bearer fake-token"}
    client.post("/habits", json={"name": "Walk", "periodicity": "weekly"}, headers=headers)
    resp = client.get("/stats", headers=headers)
    assert resp.status_code == 200
    assert "total_habits" in resp.json()


def test_unauthorized():
    resp = client.get("/habits")
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "http_error"
