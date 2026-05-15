from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from pykotmig.analyze import run_analyze
from pykotmig.codegen.emit import emit_project


@pytest.mark.skipif(shutil.which("java") is None, reason="JDK not on PATH")
def test_generate_order_api_passes_gradle_test(tmp_path: Path) -> None:
    repo = Path(__file__).resolve().parents[2]
    a = run_analyze(repo / "examples/order-api/python", "order_api.app:app", force=True)
    out = tmp_path / "gen-order"
    emit_project(
        a,
        out=out,
        kotlin_package="dev.pykotmig.gen.orderapi",
        project_name="gen-order-api",
        profile="order-api",
        force=True,
        allow_errors=False,
    )
    r = subprocess.run(
        ["bash", str(out / "gradlew"), "test", "--no-daemon", "-q"],
        cwd=str(out),
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0, r.stdout + r.stderr
