from __future__ import annotations

from pathlib import Path

from cli_batch_demo.batch import map_lines
from cli_batch_demo.cli import main


def test_map_lines_skips_blank() -> None:
    assert map_lines(["hello", "", "  \n"], str.upper) == ["HELLO"]


def test_cli_upper(tmp_path: Path) -> None:
    p = tmp_path / "in.txt"
    p.write_text("hello\n\nWorld\n", encoding="utf-8")
    assert main(["upper", "--input", str(p)]) == 0
