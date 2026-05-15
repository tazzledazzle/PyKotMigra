from __future__ import annotations

from pathlib import Path

import pytest

from pykotmig.codegen.load import CodegenError, assert_ready_for_codegen, load_analysis
from pykotmig.ir import AnalysisRoot, CliInfo, ErrorItem


def test_load_order_fixture(order_analysis_path: Path) -> None:
    a = load_analysis(order_analysis_path)
    assert a.openapi is not None
    assert "/orders" in (a.openapi.get("paths") or {})


def test_rejects_missing_openapi(tmp_path: Path) -> None:
    p = tmp_path / "a.json"
    p.write_text(
        AnalysisRoot(
            generated_at="t",
            project_root="/x",
            cli=CliInfo(version="0"),
            openapi=None,
        ).model_dump_json(),
        encoding="utf-8",
    )
    with pytest.raises(CodegenError, match="GEN_NO_OPENAPI"):
        assert_ready_for_codegen(load_analysis(p))


def test_rejects_errors_by_default(tmp_path: Path) -> None:
    p = tmp_path / "a.json"
    p.write_text(
        AnalysisRoot(
            generated_at="t",
            project_root="/x",
            cli=CliInfo(version="0"),
            openapi={"openapi": "3.1.0", "info": {"title": "x", "version": "1"}, "paths": {}},
            errors=[ErrorItem(message="boom", hint="fix", rule_id="X")],
        ).model_dump_json(),
        encoding="utf-8",
    )
    with pytest.raises(CodegenError, match="GEN_ANALYSIS_ERRORS"):
        assert_ready_for_codegen(load_analysis(p))


def test_allow_errors(tmp_path: Path) -> None:
    p = tmp_path / "a.json"
    p.write_text(
        AnalysisRoot(
            generated_at="t",
            project_root="/x",
            cli=CliInfo(version="0"),
            openapi={"openapi": "3.1.0", "info": {"title": "x", "version": "1"}, "paths": {}},
            errors=[ErrorItem(message="boom")],
        ).model_dump_json(),
        encoding="utf-8",
    )
    assert_ready_for_codegen(load_analysis(p), allow_errors=True)


@pytest.fixture
def order_analysis_path(tmp_path: Path) -> Path:
    from pykotmig.analyze import run_analyze

    repo = Path(__file__).resolve().parents[2]
    proj = repo / "examples" / "order-api" / "python"
    out = tmp_path / "order-analysis.json"
    a = run_analyze(proj, "order_api.app:app", force=True)
    out.write_text(a.model_dump_json(indent=2), encoding="utf-8")
    return out
