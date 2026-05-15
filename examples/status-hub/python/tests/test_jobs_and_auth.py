"""Background job scheduling and API-key auth (catalog v2 parity)."""

from __future__ import annotations

import time

import pytest
from fastapi.testclient import TestClient

from status_hub.app import (
    app,
    completed_job_ids,
    reset_completed_jobs_for_tests,
)


@pytest.fixture
def client() -> TestClient:
    reset_completed_jobs_for_tests()
    with TestClient(app) as c:
        yield c


def test_schedule_job_returns_202_and_completes_background(client: TestClient) -> None:
    r = client.post("/jobs")
    assert r.status_code == 202
    data = r.json()
    assert data["status"] == "accepted"
    assert "job_id" in data
    deadline = time.monotonic() + 2.0
    while time.monotonic() < deadline:
        if data["job_id"] in completed_job_ids():
            break
        time.sleep(0.01)
    assert data["job_id"] in completed_job_ids()


def test_secure_ping_ok(client: TestClient) -> None:
    r = client.get("/secure/ping", headers={"x-api-key": "demo-key"})
    assert r.status_code == 200
    assert r.json() == {"authenticated": "yes"}


def test_secure_ping_missing_key(client: TestClient) -> None:
    r = client.get("/secure/ping")
    assert r.status_code == 401


def test_secure_ping_wrong_key(client: TestClient) -> None:
    r = client.get("/secure/ping", headers={"x-api-key": "wrong"})
    assert r.status_code == 401
