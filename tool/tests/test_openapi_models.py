from __future__ import annotations

from pathlib import Path

from pykotmig.analyze import run_analyze
from pykotmig.codegen.openapi_kotlin import emit_models_kotlin


def test_status_hub_models_from_openapi() -> None:
    repo = Path(__file__).resolve().parents[2]
    a = run_analyze(repo / "examples/status-hub/python", "status_hub.app:app", force=True)
    assert a.openapi is not None
    src = emit_models_kotlin(a.openapi, "dev.test.gen")
    assert "data class HealthResponse" in src
    assert 'val status: String = "ok"' in src
    assert "data class EchoRequest" in src
    assert "val message: String" in src
    assert "val count: Int" in src
