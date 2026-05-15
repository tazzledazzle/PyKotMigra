from __future__ import annotations

import subprocess
from pathlib import Path

TOOL_ROOT = Path(__file__).resolve().parents[1]


def test_root_help_via_module() -> None:
    r = subprocess.run(
        ["uv", "run", "python", "-m", "pykotmig", "--help"],
        cwd=str(TOOL_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0, r.stderr
    assert "analyze" in r.stdout
    assert "generate" in r.stdout
    assert "verify" in r.stdout


def test_analyze_help_lists_flags() -> None:
    r = subprocess.run(
        ["uv", "run", "python", "-m", "pykotmig", "analyze", "--help"],
        cwd=str(TOOL_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0, r.stderr
    assert "--project-root" in r.stdout
    assert "--app" in r.stdout
    assert "--dry-run" in r.stdout


def test_generate_help_lists_flags() -> None:
    r = subprocess.run(
        ["uv", "run", "python", "-m", "pykotmig", "generate", "--help"],
        cwd=str(TOOL_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0, r.stderr
    assert "--analysis" in r.stdout
    assert "--profile" in r.stdout


def test_requires_pyproject(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir(parents=True)
    (tmp_path / "src/x.py").write_text("a=1\n")
    out = tmp_path / "out.json"
    r = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "-m",
            "pykotmig",
            "analyze",
            "--project-root",
            str(tmp_path),
            "--app",
            "x:app",
            "--out",
            str(out),
        ],
        cwd=str(TOOL_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode != 0
