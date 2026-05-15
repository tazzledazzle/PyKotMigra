"""Line-oriented batch transforms."""

from __future__ import annotations

from collections.abc import Callable, Iterable


def map_lines(lines: Iterable[str], fn: Callable[[str], str]) -> list[str]:
    """Apply ``fn`` to each non-empty stripped line."""
    out: list[str] = []
    for raw in lines:
        line = raw.rstrip("\n")
        if not line.strip():
            continue
        out.append(fn(line))
    return out
