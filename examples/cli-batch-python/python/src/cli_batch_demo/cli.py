"""argparse entrypoint for batch transforms."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import TextIO

from cli_batch_demo.batch import map_lines


def _read_lines(path: Path | None) -> list[str]:
    if path is None:
        return sys.stdin.read().splitlines()
    return path.read_text(encoding="utf-8").splitlines()


def _write_lines(lines: list[str], out: TextIO) -> None:
    for ln in lines:
        out.write(ln + "\n")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="cli-batch-demo", description="Batch line transforms.")
    sub = p.add_subparsers(dest="cmd", required=True)

    upper = sub.add_parser("upper", help="Uppercase each line")
    upper.add_argument("--input", type=Path, help="Input file (default: stdin)")

    lower = sub.add_parser("lower", help="Lowercase each line")
    lower.add_argument("--input", type=Path, help="Input file (default: stdin)")

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    lines = _read_lines(getattr(args, "input", None))
    if args.cmd == "upper":
        result = map_lines(lines, str.upper)
    elif args.cmd == "lower":
        result = map_lines(lines, str.lower)
    else:
        raise SystemExit(2)
    _write_lines(result, sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
