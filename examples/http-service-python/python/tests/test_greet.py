"""Greet endpoint validation coverage."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from http_service_demo.app import create_app


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())


def test_greet_empty_name_422(client: TestClient) -> None:
    r = client.post("/greet", json={"name": ""})
    assert r.status_code == 422


def test_greet_name_too_long_422(client: TestClient) -> None:
    r = client.post("/greet", json={"name": "x" * 81})
    assert r.status_code == 422


def test_greet_strips_whitespace(client: TestClient) -> None:
    r = client.post("/greet", json={"name": "  Pat  "})
    assert r.status_code == 200
    assert r.json()["message"] == "Hello, Pat"
