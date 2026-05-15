from fastapi.testclient import TestClient

from status_hub.app import app

client = TestClient(app)


def test_health() -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_version() -> None:
    r = client.get("/version")
    assert r.status_code == 200
    assert r.json()["name"] == "status-hub"
    assert r.json()["version"] == "0.1.0"


def test_echo_ok() -> None:
    r = client.post("/echo", json={"message": "hello", "count": 2})
    assert r.status_code == 200
    assert r.json() == {"message": "hello", "count": 2}


def test_echo_validation() -> None:
    r = client.post("/echo", json={"message": "", "count": 0})
    assert r.status_code == 422
