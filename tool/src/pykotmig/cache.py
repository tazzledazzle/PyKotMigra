from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CACHE_SUBDIR = Path(".pykotmig") / "cache"
STATE_NAME = "file_state.json"


def cache_dir(project_root: Path) -> Path:
    return project_root / CACHE_SUBDIR


def state_path(project_root: Path) -> Path:
    return cache_dir(project_root) / STATE_NAME


def load_file_state(project_root: Path) -> dict[str, Any]:
    p = state_path(project_root)
    if not p.is_file():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_file_state(project_root: Path, state: dict[str, Any]) -> None:
    d = cache_dir(project_root)
    d.mkdir(parents=True, exist_ok=True)
    state_path(project_root).write_text(json.dumps(state, indent=2), encoding="utf-8")


def get_cached_record(state: dict[str, Any], rel_path: str, sha256: str) -> dict[str, Any] | None:
    entry = state.get(rel_path)
    if not isinstance(entry, dict):
        return None
    if entry.get("sha256") != sha256:
        return None
    rec = entry.get("record")
    return rec if isinstance(rec, dict) else None


def put_cached_record(state: dict[str, Any], rel_path: str, sha256: str, record: dict[str, Any]) -> None:
    state[rel_path] = {"sha256": sha256, "record": record}
