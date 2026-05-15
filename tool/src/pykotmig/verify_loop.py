"""Run Gradle on a generated project and optionally use a cloud LLM to propose fixes."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.parse import unquote

import httpx
from pydantic import BaseModel, Field


class LlmFixResponse(BaseModel):
    explanation: str = ""
    files: dict[str, str] = Field(default_factory=dict)


def run_gradle(project_dir: Path, gradle_args: list[str], *, timeout_sec: int = 600) -> tuple[int, str]:
    gw = project_dir / "gradlew"
    if not gw.is_file():
        return 127, f"No gradlew at {gw}"
    cmd = ["bash", str(gw), *gradle_args]
    r = subprocess.run(
        cmd,
        cwd=str(project_dir.resolve()),
        capture_output=True,
        text=True,
        timeout=timeout_sec,
        check=False,
    )
    log = (r.stdout or "") + "\n" + (r.stderr or "")
    return r.returncode, log


def _strip_json_fence(raw: str) -> str:
    t = raw.strip()
    if t.startswith("```"):
        t = re.sub(r"^```(?:json)?\s*", "", t)
        t = re.sub(r"\s*```$", "", t)
    return t.strip()


def _parse_llm_json(content: str) -> LlmFixResponse:
    cleaned = _strip_json_fence(content)
    data: Any = json.loads(cleaned)
    if not isinstance(data, dict):
        raise ValueError("LLM JSON root must be an object")
    return LlmFixResponse.model_validate(data)


def _safe_project_path(project_dir: Path, rel: str) -> Path | None:
    rel = rel.replace("\\", "/").lstrip("/")
    if ".." in Path(rel).parts:
        return None
    target = (project_dir / rel).resolve()
    root = project_dir.resolve()
    if root not in target.parents and target != root:
        return None
    return target


def _normalize_rel_key(project_dir: Path, key: str) -> str | None:
    key = key.strip()
    p = Path(key)
    root = project_dir.resolve()
    if p.is_absolute():
        try:
            return p.resolve().relative_to(root).as_posix()
        except ValueError:
            return None
    rel = key.replace("\\", "/").lstrip("/")
    if ".." in Path(rel).parts:
        return None
    return rel


def apply_file_updates(project_dir: Path, files: dict[str, str]) -> list[str]:
    written: list[str] = []
    for rel_raw, text in files.items():
        rel = _normalize_rel_key(project_dir, rel_raw)
        if rel is None:
            continue
        target = _safe_project_path(project_dir, rel)
        if target is None:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        written.append(rel)
    return written


def collect_context_snippets(project_dir: Path, log: str, *, max_extra_kt: int = 4) -> dict[str, str]:
    files: dict[str, str] = {}
    for name in ("settings.gradle.kts", "build.gradle.kts"):
        p = project_dir / name
        if p.is_file():
            files[name] = p.read_text(encoding="utf-8")

    seen: set[str] = set()
    for m in re.finditer(r"e:\s*file://(.+?\.(?:kt|kts)):\d+:", log):
        raw = unquote(m.group(1))
        path = Path(raw)
        if not path.is_absolute():
            path = (project_dir / path).resolve()
        path = path.resolve()
        try:
            rel = path.relative_to(project_dir.resolve())
        except ValueError:
            continue
        key = rel.as_posix()
        if key in seen or len(seen) >= max_extra_kt:
            continue
        if path.is_file():
            files[key] = path.read_text(encoding="utf-8")
            seen.add(key)
    return files


def call_openai_fix(
    *,
    model: str,
    system: str,
    user: str,
    timeout_sec: int = 120,
) -> LlmFixResponse:
    api_key = os.environ.get("PYKOTMIG_OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Set OPENAI_API_KEY or PYKOTMIG_OPENAI_API_KEY for --llm.")

    base = (os.environ.get("OPENAI_BASE_URL") or "https://api.openai.com/v1").rstrip("/")
    url = f"{base}/chat/completions"

    payload = {
        "model": model,
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    with httpx.Client(timeout=timeout_sec) as client:
        r = client.post(url, headers=headers, json=payload)
        r.raise_for_status()
        body = r.json()

    content = body["choices"][0]["message"]["content"]
    if not isinstance(content, str):
        raise RuntimeError("Unexpected API response shape")
    return _parse_llm_json(content)


SYSTEM_PROMPT = """You fix Gradle + Kotlin JVM projects produced by a code generator.

Return ONE JSON object only (no markdown), with this exact shape:
{"explanation":"short summary of what was wrong and what you changed","files":{"path/relative/to/project/root":"FULL new file contents"}}

Rules:
- Only include entries in "files" for files you actually change.
- Prefer fixing settings.gradle.kts and build.gradle.kts for plugin or repository issues.
- You may fix at most one application Kotlin source file if the compiler error clearly requires it.
- Preserve Kotlin compilation semantics; do not delete unrelated code unless necessary to build.
"""


def _emit_verify_dry_run_debug(
    *,
    project_dir: Path,
    gradle_args: list[str],
    gradle_exit: int,
    log: str,
    ctx: dict[str, str],
    user_payload: dict[str, Any],
    llm_model: str,
    fix: LlmFixResponse,
    log_tail_chars: int = 16_000,
    context_file_max_chars: int = 12_000,
    user_json_max_chars: int = 32_000,
) -> None:
    err = sys.stderr
    base = (os.environ.get("OPENAI_BASE_URL") or "https://api.openai.com/v1").rstrip("/")
    has_key = bool(os.environ.get("PYKOTMIG_OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY"))
    err.write("\n=== pykotmig verify --llm --dry-run debug ===\n")
    err.write(f"project_dir={project_dir}\n")
    err.write(f"gradlew_argv={gradle_args!r}\n")
    err.write(f"gradle_exit_code={gradle_exit}\n")
    err.write(f"openai_base_url={base}\n")
    err.write(f"api_key_set={'yes' if has_key else 'no'}\n")
    err.write(f"llm_model={llm_model!r}\n")
    err.write("\n--- Gradle log (tail) ---\n")
    tail = log[-log_tail_chars:] if len(log) > log_tail_chars else log
    err.write(tail)
    if len(log) > len(tail):
        err.write(f"\n[... log truncated to last {log_tail_chars} chars of {len(log)} total ...]\n")
    err.write("\n--- Context snippet paths (read for LLM) ---\n")
    for rel, text in sorted(ctx.items()):
        err.write(f"  {rel}  bytes={len(text.encode('utf-8'))}\n")
    err.write("\n--- Context file contents ---\n")
    for rel, text in sorted(ctx.items()):
        err.write(f"\n### file: {rel}\n")
        if len(text) > context_file_max_chars:
            err.write(text[:context_file_max_chars])
            err.write(f"\n[... truncated file at {context_file_max_chars} chars of {len(text)} ...]\n")
        else:
            err.write(text)
        if not text.endswith("\n"):
            err.write("\n")
    err.write("\n--- LLM user JSON (gradle_tail + files) ---\n")
    uj = json.dumps(user_payload, indent=2)
    if len(uj) > user_json_max_chars:
        err.write(uj[:user_json_max_chars])
        err.write(f"\n[... truncated at {user_json_max_chars} chars of {len(uj)} ...]\n")
    else:
        err.write(uj)
    err.write("\n--- LLM response: explanation ---\n")
    err.write(fix.explanation + "\n")
    err.write("\n--- LLM response: proposed files (full contents; not written) ---\n")
    for path, body in sorted(fix.files.items()):
        err.write(f"\n### proposed path: {path}\n")
        err.write(body)
        if not body.endswith("\n"):
            err.write("\n")
    err.write("\n=== end dry-run debug ===\n")
    err.flush()


def verify_with_optional_llm(
    project_dir: Path,
    *,
    gradle_args: list[str],
    max_rounds: int,
    use_llm: bool,
    llm_model: str,
    dry_run: bool,
) -> int:
    project_dir = project_dir.resolve()
    for round_i in range(max_rounds):
        code, log = run_gradle(project_dir, gradle_args)
        if code == 0:
            return 0
        if not use_llm:
            print(log)
            return code

        ctx = collect_context_snippets(project_dir, log)
        user_payload: dict[str, Any] = {
            "gradle_exit_code": code,
            "gradle_tail": log[-24_000:],
            "files": ctx,
        }
        user = json.dumps(user_payload, indent=2)
        try:
            fix = call_openai_fix(model=llm_model, system=SYSTEM_PROMPT, user=user)
        except Exception as e:
            print(log)
            raise RuntimeError(f"LLM call failed: {e}") from e

        print(f"--- LLM round {round_i + 1} ---\n{fix.explanation}\n")
        if dry_run:
            _emit_verify_dry_run_debug(
                project_dir=project_dir,
                gradle_args=gradle_args,
                gradle_exit=code,
                log=log,
                ctx=ctx,
                user_payload=user_payload,
                llm_model=llm_model,
                fix=fix,
            )
            return code

        if not fix.files:
            print(log)
            return code

        apply_file_updates(project_dir, fix.files)

    code, log = run_gradle(project_dir, gradle_args)
    if code != 0:
        print(log)
    return code
