from __future__ import annotations

from pathlib import Path

from pykotmig.analyze import run_analyze
from pykotmig.codegen.openapi_kotlin import emit_status_hub_application


def test_status_hub_application_contains_routes() -> None:
    repo = Path(__file__).resolve().parents[2]
    a = run_analyze(repo / "examples/status-hub/python", "status_hub.app:app", force=True)
    assert a.openapi is not None
    src = emit_status_hub_application("dev.test.gen", a.openapi)
    assert 'get("/health")' in src
    assert 'post("/echo")' in src
    assert "CorrelationIdKey" in src
