from fastapi.testclient import TestClient

from status_hub.app import app

client = TestClient(app)


def test_health_golden_http() -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.text == '{"status":"ok"}'


def test_version_golden_http() -> None:
    r = client.get("/version")
    assert r.status_code == 200
    assert r.text == '{"name":"status-hub","version":"0.1.0"}'


def test_echo_ok_golden_http() -> None:
    r = client.post("/echo", json={"message": "hello", "count": 2})
    assert r.status_code == 200
    assert r.text == '{"message":"hello","count":2}'


def test_echo_validation() -> None:
    r = client.post("/echo", json={"message": "", "count": 0})
    assert r.status_code == 422
