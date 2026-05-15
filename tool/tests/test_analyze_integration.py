from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
ORDER_API_PYTHON = REPO_ROOT / "examples" / "order-api" / "python"


@pytest.fixture
def order_project() -> Path:
    assert ORDER_API_PYTHON.is_dir(), "expected examples/order-api/python in repo"
    assert (ORDER_API_PYTHON / "pyproject.toml").is_file()
    return ORDER_API_PYTHON


def test_order_api_openapi(order_project: Path) -> None:
    from pykotmig.analyze import run_analyze

    a = run_analyze(order_project, "order_api.app:app", force=True, mypy_enable=False)
    assert a.openapi is not None
    paths = a.openapi.get("paths") or {}
    assert any("orders" in k for k in paths)
    assert len(a.files) >= 1
    for f in a.files:
        if f.ast_ok:
            assert f.libcst_ok, f.path


def test_analysis_validates_against_committed_schema(order_project: Path) -> None:
    import json
    from jsonschema import Draft202012Validator

    from pykotmig.analyze import run_analyze

    schema_path = REPO_ROOT / "tool" / "schemas" / "analysis-v1.schema.json"
    assert schema_path.is_file(), "run schema export (see tool README)"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    a = run_analyze(order_project, "order_api.app:app", force=True)
    data = a.model_dump(mode="json")
    Draft202012Validator(schema).validate(data)


def test_mypy_optional(order_project: Path) -> None:
    from pykotmig.analyze import run_analyze

    r = run_analyze(order_project, "order_api.app:app", force=True, mypy_enable=True)
    assert r.mypy is not None
    assert r.mypy.attempted is True
