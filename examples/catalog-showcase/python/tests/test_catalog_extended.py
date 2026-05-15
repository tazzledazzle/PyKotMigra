"""Catalog showcase routes and helpers not covered by the smoke tests."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from catalog_showcase.app import create_app
from catalog_showcase.deps import get_settings_dep
from catalog_showcase.validation import router as validation_router


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())


def test_ready_endpoint(client: TestClient) -> None:
    r = client.get("/ready")
    assert r.status_code == 200
    assert r.json()["ready"] == "true"


def test_items_list_and_create(client: TestClient) -> None:
    r0 = client.get("/items")
    assert r0.status_code == 200
    n0 = len(r0.json())
    r1 = client.post("/items", json={"name": "x", "quantity": 0})
    assert r1.status_code == 200
    r2 = client.get("/items")
    assert len(r2.json()) == n0 + 1


def test_items_get_404(client: TestClient) -> None:
    assert client.get("/items/missing-id").status_code == 404


def test_validation_score_ok(client: TestClient) -> None:
    r = client.post("/validation-demo/score", json={"score": 50})
    assert r.status_code == 200
    assert r.json()["score"] == 50


def test_get_settings_dep() -> None:
    s = get_settings_dep()
    assert s.service_name == "catalog-showcase"


def test_validation_router_prefix() -> None:
    assert validation_router.prefix == "/validation-demo"
