"""CLI argument parsing and ``lower`` subcommand."""

from __future__ import annotations

import io
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from cli_batch_demo.cli import build_parser, main


def test_build_parser_has_subcommands(tmp_path: Path) -> None:
    p = tmp_path / "x.txt"
    p.write_text("a", encoding="utf-8")
    parser = build_parser()
    assert parser.parse_args(["upper", "--input", str(p)]).cmd == "upper"


def test_main_lower(tmp_path: Path) -> None:
    p = tmp_path / "t.txt"
    p.write_text("AbC\n", encoding="utf-8")
    assert main(["lower", "--input", str(p)]) == 0


def test_main_missing_subcommand_exits() -> None:
    with pytest.raises(SystemExit):
        main([])


def test_main_unknown_command_exits() -> None:
    with pytest.raises(SystemExit):
        main(["nope"])


def test_main_upper_writes_stdout(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    p = tmp_path / "x.txt"
    p.write_text("hi\n", encoding="utf-8")
    assert main(["upper", "--input", str(p)]) == 0
    assert capsys.readouterr().out == "HI\n"


def test_main_upper_reads_stdin(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("x\ny\n"))
    assert main(["upper"]) == 0
    assert capsys.readouterr().out == "X\nY\n"


def test_main_unknown_cmd_raises_exit_2(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    p = tmp_path / "in.txt"
    p.write_text("a\n", encoding="utf-8")

    class FakeParser:
        def parse_args(self, argv: list[str] | None) -> object:
            return SimpleNamespace(cmd="other", input=p)

    monkeypatch.setattr("cli_batch_demo.cli.build_parser", lambda: FakeParser())
    with pytest.raises(SystemExit) as exc:
        main([])
    assert exc.value.code == 2


def test_run_module_as_main(tmp_path: Path) -> None:
    p = tmp_path / "f.txt"
    p.write_text("ok\n", encoding="utf-8")
    root = Path(__file__).resolve().parents[1]
    proc = subprocess.run(
        [sys.executable, "-m", "cli_batch_demo.cli", "upper", "--input", str(p)],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    assert proc.stdout == "OK\n"
