"""Unit tests for ``notify_order_created`` (no FastAPI app)."""

from __future__ import annotations

import logging
from unittest.mock import MagicMock, patch

import httpx
import pytest

from order_api.notify_client import notify_order_created


def test_notify_skipped_when_base_url_empty(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO)
    notify_order_created(None, "oid-1")
    notify_order_created("   ", "oid-2")
    assert any("notify skipped" in r.message for r in caplog.records)


@patch("order_api.notify_client.httpx.Client")
def test_notify_http_error_is_swallowed(mock_client: MagicMock, caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.WARNING)
    ctx = MagicMock()
    ctx.__enter__.return_value.post.side_effect = httpx.ConnectError("down")
    mock_client.return_value = ctx
    notify_order_created("https://hooks.example", "oid-3")
    assert any("notify failed" in r.message for r in caplog.records)


@patch("order_api.notify_client.httpx.Client")
def test_notify_success_logs(mock_client: MagicMock, caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO)
    resp = MagicMock()
    resp.status_code = 204
    ctx = MagicMock()
    ctx.__enter__.return_value.post.return_value = resp
    mock_client.return_value = ctx
    notify_order_created("https://hooks.example", "oid-4")
    assert any("notify done" in r.message for r in caplog.records)
