"""Phase 4: committed OpenAPI snapshot matches the live FastAPI schema."""

from __future__ import annotations

import json
from pathlib import Path

from status_hub.app import app


def _contract_path() -> Path:
    return Path(__file__).resolve().parent.parent.parent / "contracts" / "openapi.json"


def test_openapi_matches_committed_contract() -> None:
    raw = _contract_path().read_text(encoding="utf-8")
    committed = json.loads(raw)
    live = app.openapi()
    assert json.dumps(committed, sort_keys=True) == json.dumps(live, sort_keys=True), (
        "Run: cd examples/status-hub/python && uv run python ../../scripts/export_openapi.py status-hub"
    )
