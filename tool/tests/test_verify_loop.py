from __future__ import annotations

from pathlib import Path

import pytest

from pykotmig.verify_loop import (
    LlmFixResponse,
    _normalize_rel_key,
    _parse_llm_json,
    _safe_project_path,
    apply_file_updates,
    run_gradle,
)


def test_parse_llm_json_plain() -> None:
    raw = '{"explanation":"x","files":{"a.kt":"line"}}'
    r = _parse_llm_json(raw)
    assert r.explanation == "x"
    assert r.files == {"a.kt": "line"}


def test_parse_llm_json_fenced() -> None:
    raw = '```json\n{"explanation":"","files":{}}\n```'
    r = _parse_llm_json(raw)
    assert r.files == {}


def test_parse_llm_json_invalid_root() -> None:
    with pytest.raises(ValueError):
        _parse_llm_json("[]")


def test_normalize_rel_key_rejects_parent() -> None:
    root = Path("/tmp/proj")
    assert _normalize_rel_key(root, "../etc/passwd") is None


def test_safe_project_path_rejects_escape() -> None:
    root = Path("/tmp/proj")
    assert _safe_project_path(root, "../x") is None


def test_apply_file_updates_writes(tmp_path: Path) -> None:
    (tmp_path / "sub").mkdir()
    apply_file_updates(tmp_path, {"sub/f.txt": "hello"})
    assert (tmp_path / "sub/f.txt").read_text() == "hello"


def test_run_gradle_missing_wrapper(tmp_path: Path) -> None:
    code, log = run_gradle(tmp_path, ["tasks"])
    assert code == 127
    assert "gradlew" in log


def test_llm_response_model_extra_ignored() -> None:
    # pydantic default: extra ignore
    r = LlmFixResponse.model_validate({"explanation": "e", "files": {}, "unknown": 1})
    assert r.explanation == "e"
