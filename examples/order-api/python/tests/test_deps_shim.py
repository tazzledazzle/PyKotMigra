"""Ensure catalog-facing ``deps`` re-exports resolve."""

from __future__ import annotations

from order_api import deps as deps_mod


def test_reexports_resolve() -> None:
    settings = deps_mod.get_settings()
    store = deps_mod.get_store()
    assert settings is not None
    assert store is not None
