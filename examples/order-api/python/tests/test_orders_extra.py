"""404 paths, notify failure paths, and store edge cases."""

from __future__ import annotations

import httpx
import pytest
import respx
from fastapi.testclient import TestClient
from httpx import Response

from order_api.app import app

client = TestClient(app)


def test_delete_missing_returns_404() -> None:
    r = client.delete("/orders/does-not-exist")
    assert r.status_code == 404
    assert r.json() == {"detail": "order not found"}


@respx.mock
def test_notify_non_success_status_still_creates_order(monkeypatch: pytest.MonkeyPatch) -> None:
    respx.post("https://example.test/notify").mock(return_value=Response(500))
    monkeypatch.setenv("EXTERNAL_HTTP_URL", "https://example.test")
    r = client.post("/orders", json={"title": "still-created"})
    assert r.status_code == 201


@respx.mock
def test_notify_connect_error_still_creates_order(monkeypatch: pytest.MonkeyPatch) -> None:
    respx.post("https://example.test/notify").mock(side_effect=httpx.ConnectError("refused"))
    monkeypatch.setenv("EXTERNAL_HTTP_URL", "https://example.test")
    r = client.post("/orders", json={"title": "with-broken-notify"})
    assert r.status_code == 201
