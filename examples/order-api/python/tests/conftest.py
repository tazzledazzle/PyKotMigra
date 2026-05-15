"""Shared fixtures for Order API tests (global in-memory store)."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _clear_order_store() -> None:
    from order_api.app import _store

    _store.orders.clear()
    yield
    _store.orders.clear()
