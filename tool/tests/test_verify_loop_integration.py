"""Integration-style coverage for verify_loop (mocked Gradle / HTTP)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx
import pytest

from pykotmig.verify_loop import (
    LlmFixResponse,
    _emit_verify_dry_run_debug,
    _normalize_rel_key,
    call_openai_fix,
    collect_context_snippets,
    verify_with_optional_llm,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
STATUS_HUB_KOTLIN = REPO_ROOT / "examples" / "status-hub" / "kotlin"


def test_collect_context_snippets_includes_gradle_files(tmp_path: Path) -> None:
    (tmp_path / "settings.gradle.kts").write_text("rootProject.name = \"x\"\n")
    (tmp_path / "build.gradle.kts").write_text("plugins { kotlin(\"jvm\") }\n")
    log = f"e: file://{tmp_path / 'src/Main.kt'}:10: error"
    ctx = collect_context_snippets(tmp_path, log, max_extra_kt=2)
    assert "settings.gradle.kts" in ctx
    assert "build.gradle.kts" in ctx


def test_normalize_rel_key_absolute_inside_project(tmp_path: Path) -> None:
    kt = tmp_path / "src/Foo.kt"
    kt.parent.mkdir(parents=True)
    kt.write_text("x")
    rel = _normalize_rel_key(tmp_path, str(kt.resolve()))
    assert rel == "src/Foo.kt"


def test_call_openai_fix_mocked(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    body = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(
                        {"explanation": "fix", "files": {"build.gradle.kts": "ok"}}
                    )
                }
            }
        ]
    }
    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.post.return_value = httpx.Response(
        200,
        json=body,
        request=httpx.Request("POST", "https://api.openai.com/v1/chat/completions"),
    )
    with patch("httpx.Client", return_value=mock_client):
        fix = call_openai_fix(model="gpt-test", system="sys", user="user")
    assert fix.explanation == "fix"
    assert "build.gradle.kts" in fix.files


def test_verify_success_first_gradle_run() -> None:
    with patch("pykotmig.verify_loop.run_gradle", return_value=(0, "ok")):
        code = verify_with_optional_llm(
            STATUS_HUB_KOTLIN,
            gradle_args=["test"],
            max_rounds=2,
            use_llm=False,
            llm_model="gpt-test",
            dry_run=False,
        )
    assert code == 0


def test_verify_llm_round_applies_patch(tmp_path: Path) -> None:
    (tmp_path / "gradlew").write_text("#!/bin/sh\nexit 0\n")
    (tmp_path / "gradlew").chmod(0o755)
    (tmp_path / "build.gradle.kts").write_text("broken\n")

    fix = LlmFixResponse(explanation="patched", files={"build.gradle.kts": "fixed\n"})
    calls = [0]

    def fake_gradle(project_dir: Path, args: list[str], **kw: object) -> tuple[int, str]:
        calls[0] += 1
        if calls[0] == 1:
            return 1, f"e: file://{project_dir / 'build.gradle.kts'}:1: err"
        return 0, "BUILD SUCCESSFUL"

    with (
        patch("pykotmig.verify_loop.run_gradle", side_effect=fake_gradle),
        patch("pykotmig.verify_loop.call_openai_fix", return_value=fix),
    ):
        code = verify_with_optional_llm(
            tmp_path,
            gradle_args=["test"],
            max_rounds=2,
            use_llm=True,
            llm_model="gpt-test",
            dry_run=False,
        )
    assert code == 0
    assert (tmp_path / "build.gradle.kts").read_text() == "fixed\n"


def test_verify_llm_dry_run_emits_debug(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    fix = LlmFixResponse(explanation="dry", files={})
    with (
        patch("pykotmig.verify_loop.run_gradle", return_value=(1, "fail log")),
        patch("pykotmig.verify_loop.call_openai_fix", return_value=fix),
    ):
        code = verify_with_optional_llm(
            tmp_path,
            gradle_args=["test"],
            max_rounds=1,
            use_llm=True,
            llm_model="gpt-test",
            dry_run=True,
        )
    assert code == 1
    err = capsys.readouterr().err
    assert "dry-run debug" in err


def test_emit_verify_dry_run_debug_truncation(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    big = "x" * 20_000
    _emit_verify_dry_run_debug(
        project_dir=tmp_path,
        gradle_args=["test"],
        gradle_exit=1,
        log=big,
        ctx={"huge.kt": big},
        user_payload={"gradle_tail": big, "files": {}},
        llm_model="m",
        fix=LlmFixResponse(explanation="e", files={"out.kt": big}),
        log_tail_chars=100,
        context_file_max_chars=100,
        user_json_max_chars=100,
    )
    err = capsys.readouterr().err
    assert "truncated" in err
