from __future__ import annotations

import json
from pathlib import Path

import pytest

from pykotmig.openapi_load import load_openapi_dict


def test_unknown_openapi_source_errors(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PYKOTMIG_OPENAPI_SOURCE", "nosuch")
    spec, errs = load_openapi_dict(tmp_path, "app:app")
    assert spec is None
    assert any(e.rule_id == "BAD_OPENAPI_SOURCE" for e in errs)


def test_ollama_path_uses_mocked_http(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PYKOTMIG_OPENAPI_SOURCE", "ollama")
    (tmp_path / "src").mkdir(parents=True)
    (tmp_path / "src" / "main.py").write_text("from fastapi import FastAPI\napp = FastAPI()\n", encoding="utf-8")

    want = {
        "openapi": "3.1.0",
        "info": {"title": "Demo", "version": "0.0.1"},
        "paths": {"/hello": {"get": {"responses": {"200": {"description": "ok"}}}}},
    }

    class FakeResp:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {"message": {"role": "assistant", "content": json.dumps(want)}}

    class FakeClient:
        def __init__(self, *a: object, **kw: object) -> None:
            pass

        def __enter__(self) -> FakeClient:
            return self

        def __exit__(self, *a: object) -> None:
            return None

        def post(self, url: str, json: dict | None = None, **kw: object) -> FakeResp:
            assert "/api/chat" in url
            assert json is not None
            assert json.get("format") == "json"
            return FakeResp()

    monkeypatch.setattr("pykotmig.openapi_load.httpx.Client", FakeClient)

    spec, errs = load_openapi_dict(tmp_path, "main:app")
    assert errs == []
    assert spec == want


def test_ollama_dry_run_skips_http(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import io

    monkeypatch.setenv("PYKOTMIG_OPENAPI_SOURCE", "ollama")
    (tmp_path / "src").mkdir(parents=True)
    (tmp_path / "src" / "main.py").write_text("x=1\n", encoding="utf-8")

    called: list[str] = []

    class FakeClient:
        def __init__(self, *a: object, **kw: object) -> None:
            pass

        def __enter__(self) -> FakeClient:
            return self

        def __exit__(self, *a: object) -> None:
            return None

        def post(self, *a: object, **kw: object) -> object:
            called.append("post")
            raise AssertionError("HTTP should not be used in dry_run")

    monkeypatch.setattr("pykotmig.openapi_load.httpx.Client", FakeClient)

    buf = io.StringIO()
    spec, errs = load_openapi_dict(tmp_path, "main:app", dry_run=True, debug_stream=buf)
    assert spec is None and errs == []
    assert called == []
    out = buf.getvalue()
    assert "dry_run" in out
    assert "api/chat" in out


def test_fastapi_dry_run_skips_import(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import io

    monkeypatch.setenv("PYKOTMIG_OPENAPI_SOURCE", "fastapi")
    buf = io.StringIO()
    spec, errs = load_openapi_dict(tmp_path, "missing_mod:app", dry_run=True, debug_stream=buf)
    assert spec is None and errs == []
    assert "fastapi" in buf.getvalue().lower()


def test_ollama_no_src_errors(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PYKOTMIG_OPENAPI_SOURCE", "ollama")
    (tmp_path / "lib").mkdir()
    spec, errs = load_openapi_dict(tmp_path, "x:y")
    assert spec is None
    assert any(e.rule_id == "OPENAPI_OLLAMA_NO_SRC" for e in errs)
