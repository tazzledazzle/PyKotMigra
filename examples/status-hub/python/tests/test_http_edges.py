"""Extra HTTP / validation coverage for Status Hub."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from status_hub.app import app

client = TestClient(app)


@pytest.mark.parametrize(
    ("payload", "desc"),
    [
        ({"message": "ok", "count": 101}, "count above max"),
        ({"message": "ok", "count": 0}, "count below min"),
        ({"message": "", "count": 1}, "empty message"),
    ],
)
def test_echo_validation_variants(payload: dict[str, int | str], desc: str) -> None:
    r = client.post("/echo", json=payload)
    assert r.status_code == 422, desc


def test_echo_strips_message_in_response() -> None:
    r = client.post("/echo", json={"message": "  spaced  ", "count": 1})
    assert r.status_code == 200
    assert r.json()["message"] == "spaced"


def test_correlation_id_roundtrip() -> None:
    r = client.get("/health", headers={"x-correlation-id": "trace-123"})
    assert r.status_code == 200
    assert r.headers.get("x-correlation-id") == "trace-123"


def test_correlation_id_generated_when_absent() -> None:
    r = client.get("/health")
    assert r.status_code == 200
    cid = r.headers.get("x-correlation-id")
    assert cid is not None and len(cid) > 4
