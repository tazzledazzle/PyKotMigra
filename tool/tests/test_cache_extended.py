"""Additional cache module branches."""

from __future__ import annotations

import json
from pathlib import Path

from pykotmig.cache import (
    get_cached_record,
    load_file_state,
    put_cached_record,
    save_file_state,
)


def test_load_file_state_missing_returns_empty(tmp_path: Path) -> None:
    assert load_file_state(tmp_path) == {}


def test_load_file_state_invalid_json(tmp_path: Path) -> None:
    from pykotmig.cache import cache_dir, state_path

    cache_dir(tmp_path).mkdir(parents=True)
    state_path(tmp_path).write_text("{not json", encoding="utf-8")
    assert load_file_state(tmp_path) == {}


def test_get_cached_record_sha_mismatch(tmp_path: Path) -> None:
    state: dict = {}
    put_cached_record(state, "a.py", "sha1", {"ok": True})
    assert get_cached_record(state, "a.py", "sha2") is None


def test_get_cached_record_bad_entry_shape() -> None:
    state = {"a.py": "not-a-dict"}
    assert get_cached_record(state, "a.py", "sha") is None


def test_save_and_roundtrip(tmp_path: Path) -> None:
    state = {"f.py": {"sha256": "abc", "record": {"path": "f.py"}}}
    save_file_state(tmp_path, state)
    loaded = load_file_state(tmp_path)
    assert loaded["f.py"]["sha256"] == "abc"
    assert json.loads((tmp_path / ".pykotmig/cache/file_state.json").read_text()) == loaded
