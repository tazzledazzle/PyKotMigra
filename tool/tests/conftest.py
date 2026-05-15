from __future__ import annotations

import os

import pytest


@pytest.fixture(autouse=True)
def _default_openapi_via_fastapi(monkeypatch: pytest.MonkeyPatch) -> None:
    """Tests expect deterministic FastAPI ``app.openapi()`` unless they opt into Ollama."""
    if os.environ.get("PYKOTMIG_OPENAPI_SOURCE") is None:
        monkeypatch.setenv("PYKOTMIG_OPENAPI_SOURCE", "fastapi")
