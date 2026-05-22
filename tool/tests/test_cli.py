"""CLI smoke tests — introspect Typer/Click options (stable in CI; no help-text parsing)."""

from __future__ import annotations

from pathlib import Path

import click
from typer.main import get_command
from typer.testing import CliRunner

from pykotmig.cli.main import app

TOOL_ROOT = Path(__file__).resolve().parents[1]
runner = CliRunner()


def _option_flags(command_name: str) -> set[str]:
    cmd = get_command(app)
    sub = cmd.commands[command_name]
    flags: set[str] = set()
    for param in sub.params:
        if isinstance(param, click.Option):
            flags.update(param.opts)
    return flags


def test_root_lists_subcommands() -> None:
    cmd = get_command(app)
    assert {"analyze", "generate", "verify"}.issubset(cmd.commands.keys())


def test_analyze_help_lists_flags() -> None:
    flags = _option_flags("analyze")
    assert {"--project-root", "--app", "--dry-run"}.issubset(flags)


def test_generate_help_lists_flags() -> None:
    flags = _option_flags("generate")
    assert {"--analysis", "--profile"}.issubset(flags)


def test_analyze_help_invocation_exits_zero() -> None:
    """Smoke: Typer help still runs (stdout format varies by TTY/CI)."""
    result = runner.invoke(app, ["analyze", "--help"])
    assert result.exit_code == 0


def test_generate_help_invocation_exits_zero() -> None:
    result = runner.invoke(app, ["generate", "--help"])
    assert result.exit_code == 0


def test_requires_pyproject(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir(parents=True)
    (tmp_path / "src/x.py").write_text("a=1\n")
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
