from __future__ import annotations

from fastapi.testclient import TestClient

from http_service_demo.app import create_app


def test_health() -> None:
    c = TestClient(create_app())
    r = c.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_greet() -> None:
    c = TestClient(create_app())
    r = c.post("/greet", json={"name": "Ada"})
    assert r.status_code == 200
    assert "Ada" in r.json()["message"]
