from uuid import UUID

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_rfc7807_format():
    headers = {"Authorization": "Bearer fake-token"}
    response = client.get("/habits/999", headers=headers)
    assert response.status_code == 404
    data = response.json()
    assert data["type"] == "about:blank"
    assert data["title"] == "Not found"
    assert data["status"] == 404
    assert data["detail"] == "Habit not found"
    assert "correlation_id" in data
    assert UUID(data["correlation_id"])


def test_rfc7807_no_stack_leak():
    headers = {"Authorization": "Bearer fake-token"}
    response = client.get("/habits/999", headers=headers)
    assert "traceback" not in response.text.lower()
    assert "exception" not in response.text.lower()
