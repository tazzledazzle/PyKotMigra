"""In-process Typer CLI coverage (complements subprocess help tests)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from pykotmig.cli.main import app

REPO_ROOT = Path(__file__).resolve().parents[2]
ORDER_API_PYTHON = REPO_ROOT / "examples" / "order-api" / "python"
STATUS_HUB_KOTLIN = REPO_ROOT / "examples" / "status-hub" / "kotlin"

runner = CliRunner()


def test_analyze_dry_run_order_api(tmp_path: Path) -> None:
    fake_openapi = {"openapi": "3.1.0", "info": {"title": "t", "version": "0"}, "paths": {}}
    with patch(
        "pykotmig.analyze.load_openapi_dict",
        return_value=(fake_openapi, []),
    ):
        result = runner.invoke(
            app,
            [
                "analyze",
                "--project-root",
                str(ORDER_API_PYTHON),
                "--app",
                "order_api.app:app",
                "--out",
                str(tmp_path / "out.json"),
                "--dry-run",
            ],
        )
    assert result.exit_code == 0, result.stdout + result.stderr
    data = json.loads(result.stdout)
    assert data.get("openapi") == fake_openapi
    assert len(data.get("files") or []) >= 1


def test_analyze_writes_out_file(tmp_path: Path) -> None:
    _mini_project(tmp_path)
    out = tmp_path / "analysis.json"
    with patch("pykotmig.analyze.load_openapi_dict", return_value=({"openapi": "3.1.0"}, [])):
        result = runner.invoke(
            app,
            [
                "analyze",
                "--project-root",
                str(tmp_path),
                "--app",
                "mini.app:app",
                "--out",
                str(out),
            ],
        )
    assert result.exit_code == 0
    assert out.is_file()
    assert "Wrote" in result.stderr or "Wrote" in result.stdout


def _mini_project(root: Path) -> None:
    (root / "pyproject.toml").write_text('[project]\nname="mini"\nversion="0"\n', encoding="utf-8")
    (root / "src/mini").mkdir(parents=True)
    (root / "src/mini/app.py").write_text(
        "from fastapi import FastAPI\napp = FastAPI()\n",
        encoding="utf-8",
    )


def test_analyze_missing_pyproject(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    result = runner.invoke(
        app,
        [
            "analyze",
            "--project-root",
            str(tmp_path),
            "--app",
            "x:app",
            "--out",
            str(tmp_path / "out.json"),
        ],
    )
    assert result.exit_code == 1
    assert "pyproject.toml" in result.stderr


def test_analyze_missing_src(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\nversion='0'\n")
    result = runner.invoke(
        app,
        [
            "analyze",
            "--project-root",
            str(tmp_path),
            "--app",
            "x:app",
            "--out",
            str(tmp_path / "out.json"),
        ],
    )
    assert result.exit_code == 1
    assert "src/" in result.stderr


def test_generate_codegen_error(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text('{"schema_version":1,"openapi":null,"errors":[{"message":"x"}]}', encoding="utf-8")
    result = runner.invoke(
        app,
        [
            "generate",
            "--analysis",
            str(bad),
            "--out",
            str(tmp_path / "out"),
            "--kotlin-package",
            "dev.test",
            "--profile",
            "status-hub",
        ],
    )
    assert result.exit_code == 1


def test_generate_bad_profile(tmp_path: Path, order_analysis_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "generate",
            "--analysis",
            str(order_analysis_path),
            "--out",
            str(tmp_path / "gen"),
            "--kotlin-package",
            "dev.test",
            "--profile",
            "not-a-profile",
        ],
    )
    assert result.exit_code == 1
    assert "status-hub or order-api" in result.stderr


def test_generate_status_hub(tmp_path: Path) -> None:
    from pykotmig.analyze import run_analyze

    analysis = tmp_path / "analysis.json"
    out = tmp_path / "out-kotlin"
    a = run_analyze(STATUS_HUB_KOTLIN.parent / "python", "status_hub.app:app", force=True)
    analysis.write_text(a.model_dump_json(indent=2), encoding="utf-8")
    result = runner.invoke(
        app,
        [
            "generate",
            "--analysis",
            str(analysis),
            "--out",
            str(out),
            "--kotlin-package",
            "dev.pykotmig.gen.test",
            "--profile",
            "status-hub",
            "--force",
        ],
    )
    assert result.exit_code == 0, result.stderr
    assert (out / "gradlew").is_file()


def test_verify_gradle_success() -> None:
    with patch("pykotmig.verify_loop.run_gradle", return_value=(0, "BUILD SUCCESSFUL")):
        result = runner.invoke(
            app,
            [
                "verify",
                "--project",
                str(STATUS_HUB_KOTLIN),
            ],
        )
    assert result.exit_code == 0


def test_verify_gradle_failure_no_llm() -> None:
    with patch("pykotmig.verify_loop.run_gradle", return_value=(1, "FAILURE: Build failed")):
        result = runner.invoke(
            app,
            [
                "verify",
                "--project",
                str(STATUS_HUB_KOTLIN),
            ],
        )
    assert result.exit_code == 1


@pytest.fixture
def order_analysis_path(tmp_path: Path) -> Path:
    from pykotmig.analyze import run_analyze

    p = tmp_path / "analysis.json"
    a = run_analyze(ORDER_API_PYTHON, "order_api.app:app", force=True)
    p.write_text(a.model_dump_json(indent=2), encoding="utf-8")
    return p
