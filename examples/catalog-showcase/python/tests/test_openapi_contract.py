"""Committed OpenAPI snapshot matches the live FastAPI schema."""

from __future__ import annotations

import json
from pathlib import Path

from catalog_showcase.app import app


def _contract_path() -> Path:
    return Path(__file__).resolve().parent.parent.parent / "contracts" / "openapi.json"


def test_openapi_matches_committed_contract() -> None:
    committed = json.loads(_contract_path().read_text(encoding="utf-8"))
    live = app.openapi()
    assert json.dumps(committed, sort_keys=True) == json.dumps(live, sort_keys=True), (
        "Run: cd examples/catalog-showcase/python && "
        "uv run python ../../scripts/export_openapi.py catalog-showcase"
    )
