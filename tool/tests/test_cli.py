from __future__ import annotations

import subprocess
import sys
from pathlib import Path

TOOL_ROOT = Path(__file__).resolve().parents[1]


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    """Run the installed CLI in-process (avoid nested ``uv run`` in CI)."""
    return subprocess.run(
        [sys.executable, "-m", "pykotmig", *args],
        cwd=str(TOOL_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )


def _combined_output(result: subprocess.CompletedProcess[str]) -> str:
    return result.stdout + result.stderr


def test_root_help_via_module() -> None:
    r = _run_cli("--help")
    assert r.returncode == 0, r.stderr
    out = _combined_output(r)
    assert "analyze" in out
    assert "generate" in out
    assert "verify" in out


def test_analyze_help_lists_flags() -> None:
    r = _run_cli("analyze", "--help")
    assert r.returncode == 0, r.stderr
    out = _combined_output(r)
    assert "--project-root" in out
    assert "--app" in out
    assert "--dry-run" in out


def test_generate_help_lists_flags() -> None:
    r = _run_cli("generate", "--help")
    assert r.returncode == 0, r.stderr
    out = _combined_output(r)
    assert "--analysis" in out
    assert "--profile" in out


def test_requires_pyproject(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir(parents=True)
    (tmp_path / "src/x.py").write_text("a=1\n")
    out = tmp_path / "out.json"
    r = _run_cli(
        "analyze",
        "--project-root",
        str(tmp_path),
        "--app",
        "x:app",
        "--out",
        str(out),
    )
    assert r.returncode != 0
