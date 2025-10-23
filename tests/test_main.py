from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_upload_invalid_file():
    headers = {"Authorization": "Bearer fake-token"}
    response = client.post(
        "/upload",
        files={"file": ("test.txt", b"not_an_image")},
        headers=headers,
    )
    assert response.status_code == 400
    data = response.json()
    assert data["type"] == "about:blank"
    assert data["title"] == "Invalid file"
    assert data["detail"] == "bad_type"
    assert "correlation_id" in data
