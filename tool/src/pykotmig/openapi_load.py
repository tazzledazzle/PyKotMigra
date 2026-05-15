from __future__ import annotations

import importlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, TextIO

import httpx

from pykotmig.ir import ErrorItem

OLLAMA_SYSTEM = """You infer an OpenAPI 3.x specification from the Python source files of a FastAPI-style project.

Return ONE JSON object only (OpenAPI document). It MUST include top-level keys: "openapi" (string, e.g. "3.1.0"), "info" (object with at least "title" and "version"), and "paths" (object; use empty {} only if there are truly no HTTP routes).

Mirror routes, methods, path parameters, request bodies, and response schemas implied by the code. Prefer accuracy over completeness for undocumented handlers."""


def _emit_openapi_debug(
    label: str,
    lines: list[str],
    *,
    stream: TextIO,
) -> None:
    stream.write(f"\n[pykotmig openapi {label}]\n")
    for line in lines:
        stream.write(line)
        if not line.endswith("\n"):
            stream.write("\n")
    stream.flush()


def _strip_json_fence(raw: str) -> str:
    t = raw.strip()
    if t.startswith("```"):
        t = re.sub(r"^```(?:json)?\s*", "", t)
        t = re.sub(r"\s*```$", "", t)
    return t.strip()


def _openapi_source_mode() -> str:
    v = (os.environ.get("PYKOTMIG_OPENAPI_SOURCE") or "ollama").strip().lower()
    return v


def _collect_src_bundle(project_root: Path, *, max_chars: int = 120_000) -> tuple[str, list[str]]:
    root = project_root.resolve()
    src = root / "src"
    if not src.is_dir():
        return "", []
    paths = sorted(p for p in src.rglob("*.py") if p.is_file())
    chunks: list[str] = []
    used: list[str] = []
    total = 0
    for p in paths:
        rel = p.relative_to(root).as_posix()
        header = f"\n\n===== {rel} =====\n"
        body = p.read_text(encoding="utf-8", errors="replace")
        piece = header + body
        if total + len(piece) > max_chars:
            chunks.append(
                f"\n\n[... truncated after {max_chars} characters; "
                f"{len(paths) - len(used)} files not included ...]\n"
            )
            break
        chunks.append(piece)
        used.append(rel)
        total += len(piece)
    return "".join(chunks), used


def _minimal_openapi_dict(obj: Any) -> dict[str, Any] | None:
    if not isinstance(obj, dict):
        return None
    if not isinstance(obj.get("openapi"), str):
        return None
    info = obj.get("info")
    if not isinstance(info, dict):
        return None
    if not isinstance(info.get("title"), str) or not isinstance(info.get("version"), str):
        return None
    out = dict(obj)
    paths = out.get("paths")
    if paths is None:
        out["paths"] = {}
    elif not isinstance(paths, dict):
        return None
    return out


def _parse_ollama_message_content(content: Any) -> dict[str, Any] | None:
    if content is None:
        return None
    if isinstance(content, dict):
        return _minimal_openapi_dict(content)
    if not isinstance(content, str):
        return None
    try:
        data = json.loads(_strip_json_fence(content))
    except json.JSONDecodeError:
        return None
    return _minimal_openapi_dict(data)


def build_ollama_openapi_request(
    project_root: Path,
    app_spec: str,
    *,
    bundle_and_files: tuple[str, list[str]] | None = None,
) -> tuple[str, dict[str, Any], list[str], str]:
    """Build Ollama ``/api/chat`` URL and JSON body; return (url, payload, files_used, user_message_json)."""
    if bundle_and_files is not None:
        bundle, files_used = bundle_and_files
    else:
        bundle, files_used = _collect_src_bundle(project_root)
    base = (
        os.environ.get("PYKOTMIG_OLLAMA_HOST") or os.environ.get("OLLAMA_HOST") or "http://127.0.0.1:11434"
    ).rstrip("/")
    model = (
        os.environ.get("PYKOTMIG_OLLAMA_MODEL")
        or os.environ.get("OLLAMA_MODEL")
        or "llama3.2"
    )
    user_obj = {
        "app_spec": app_spec,
        "instruction": "Infer OpenAPI from these project files.",
        "files_included": files_used,
        "sources": bundle,
    }
    user_json = json.dumps(user_obj, indent=2)
    url = f"{base}/api/chat"
    payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": OLLAMA_SYSTEM},
            {"role": "user", "content": user_json},
        ],
        "stream": False,
        "format": "json",
    }
    return url, payload, files_used, user_json


def _ollama_dry_run_debug_lines(
    url: str,
    payload: dict[str, Any],
    files_used: list[str],
    user_json: str,
    *,
    preview_chars: int = 4000,
) -> list[str]:
    model = payload.get("model")
    msgs = payload.get("messages") or []
    sys_len = len((msgs[0] or {}).get("content", "")) if msgs else 0
    lines = [
        f"mode=ollama dry_run (no HTTP request sent)",
        f"url={url}",
        f"model={model!r}",
        f"files_included_count={len(files_used)}",
        f"files_included={files_used!r}",
        f"system_prompt_chars={sys_len}",
        f"user_message_json_bytes={len(user_json.encode('utf-8'))}",
        f"payload_keys={sorted(payload.keys())!r}",
        f"--- user message JSON preview (first {preview_chars} chars) ---",
        user_json[:preview_chars] + ("…\n[truncated]\n" if len(user_json) > preview_chars else ""),
    ]
    return lines


def _ollama_chat_openapi(
    project_root: Path,
    app_spec: str,
    *,
    dry_run: bool,
    debug_stream: TextIO | None,
) -> tuple[dict[str, Any] | None, list[ErrorItem]]:
    bundle, files_used = _collect_src_bundle(project_root)
    if not bundle.strip():
        return None, [
            ErrorItem(
                message="No Python sources under src/ to send to Ollama.",
                hint="Ensure the project has a src/ tree with .py files, or set PYKOTMIG_OPENAPI_SOURCE=fastapi "
                "to load OpenAPI by importing the FastAPI app.",
                rule_id="OPENAPI_OLLAMA_NO_SRC",
            )
        ]

    url, payload, files_used, user_json = build_ollama_openapi_request(
        project_root, app_spec, bundle_and_files=(bundle, files_used)
    )
    stream = debug_stream if debug_stream is not None else sys.stderr

    if dry_run:
        _emit_openapi_debug(
            "dry-run",
            _ollama_dry_run_debug_lines(url, payload, files_used, user_json),
            stream=stream,
        )
        return None, []

    timeout = float(os.environ.get("PYKOTMIG_OLLAMA_TIMEOUT_SEC", "300"))
    try:
        with httpx.Client(timeout=timeout) as client:
            r = client.post(url, json=payload)
            r.raise_for_status()
            body = r.json()
    except httpx.HTTPError as e:
        return None, [
            ErrorItem(
                message=f"Ollama request failed: {e}",
                hint=f"Start Ollama locally or set OLLAMA_HOST / PYKOTMIG_OLLAMA_HOST. "
                f"To skip Ollama, set PYKOTMIG_OPENAPI_SOURCE=fastapi. Model: {payload.get('model')!r}.",
                rule_id="OPENAPI_OLLAMA_HTTP",
            )
        ]
    except json.JSONDecodeError as e:
        return None, [
            ErrorItem(
                message=f"Ollama returned invalid JSON: {e}",
                hint="Check Ollama version and model; try a different PYKOTMIG_OLLAMA_MODEL.",
                rule_id="OPENAPI_OLLAMA_PARSE",
            )
        ]

    content = (body.get("message") or {}).get("content")
    spec = _parse_ollama_message_content(content)
    if spec is None:
        raw_preview = repr(content)[:2000] if content is not None else "None"
        _emit_openapi_debug(
            "parse-failure",
            [
                "Ollama response did not yield a valid OpenAPI object.",
                f"raw_message_content_preview={raw_preview}",
            ],
            stream=stream,
        )
        return None, [
            ErrorItem(
                message="Ollama response was not a valid OpenAPI object (expected openapi, info.title/version, paths).",
                hint="Retry with a larger model or simplify src/; or use PYKOTMIG_OPENAPI_SOURCE=fastapi.",
                rule_id="OPENAPI_OLLAMA_SHAPE",
            )
        ]
    return spec, []


def _load_openapi_via_fastapi_import(project_root: Path, app_spec: str) -> tuple[dict[str, Any] | None, list[ErrorItem]]:
    """Import ``module:attr`` and call ``.openapi()`` on the FastAPI app. Trusted local use only."""
    mod_name, attr_name = app_spec.split(":", 1)
    root = project_root.resolve()
    src = root / "src"
    to_add: list[str] = []
    for p in (str(src), str(root)):
        if p not in sys.path:
            sys.path.insert(0, p)
            to_add.append(p)

    try:
        module = importlib.import_module(mod_name)
        app_obj = getattr(module, attr_name, None)
        if app_obj is None:
            return None, [
                ErrorItem(
                    path=None,
                    message=f"Attribute {attr_name!r} not found on module {mod_name!r}.",
                    hint="Check --app points at the module path under src/ and the exported FastAPI instance name.",
                    rule_id="OPENAPI_IMPORT",
                )
            ]
        openapi_fn = getattr(app_obj, "openapi", None)
        if openapi_fn is None or not callable(openapi_fn):
            return None, [
                ErrorItem(
                    message=f"Object {mod_name}:{attr_name} has no callable openapi().",
                    hint="Ensure --app references a FastAPI application instance.",
                    rule_id="OPENAPI_NOT_FASTAPI",
                )
            ]
        spec = openapi_fn()
        if not isinstance(spec, dict):
            return None, [
                ErrorItem(
                    message="openapi() did not return a dict.",
                    hint="Upgrade FastAPI or check custom openapi override.",
                    rule_id="OPENAPI_SHAPE",
                )
            ]
        return spec, []
    except Exception as e:  # noqa: BLE001 — surface to user as SCO-04
        return None, [
            ErrorItem(
                message=f"Failed to import or build OpenAPI: {e}",
                hint="Run from project root with dependencies installed (uv sync in the target project). "
                "This tool executes arbitrary import side effects — use only on trusted code.",
                rule_id="OPENAPI_IMPORT",
            )
        ]
    finally:
        for p in to_add:
            if p in sys.path:
                sys.path.remove(p)


def load_openapi_dict(
    project_root: Path,
    app_spec: str,
    *,
    dry_run: bool = False,
    debug_stream: TextIO | None = None,
) -> tuple[dict[str, Any] | None, list[ErrorItem]]:
    """Load OpenAPI as JSON.

    Default (**PYKOTMIG_OPENAPI_SOURCE** unset or ``ollama``): POST to local **Ollama** ``/api/chat`` with
    ``src/**/*.py`` context and ``--app`` as a hint. Set **OLLAMA_HOST** (or **PYKOTMIG_OLLAMA_HOST**),
    **PYKOTMIG_OLLAMA_MODEL** (or **OLLAMA_MODEL**).

    When ``dry_run`` is True, no HTTP request is sent for the Ollama path; debug lines are written to
    ``debug_stream`` (default ``sys.stderr``). OpenAPI in the result is ``None``.

    Legacy: ``PYKOTMIG_OPENAPI_SOURCE=fastapi`` imports ``module:attr`` and calls ``app.openapi()`` (trusted code).
    With ``dry_run`` and fastapi mode, import is skipped and debug is printed instead.
    """
    errors: list[ErrorItem] = []
    stream = debug_stream if debug_stream is not None else sys.stderr

    if ":" not in app_spec:
        return None, [
            ErrorItem(
                message=f"Invalid --app {app_spec!r}; expected module:attr (e.g. order_api.app:app).",
                hint="Pass the module containing your FastAPI instance and its attribute name, separated by ':'.",
                rule_id="BAD_APP_SPEC",
            )
        ]
    mod_name, attr_name = app_spec.split(":", 1)
    if not mod_name or not attr_name:
        return None, [
            ErrorItem(
                message="Empty module or attribute in --app.",
                hint="Use e.g. order_api.app:app",
                rule_id="BAD_APP_SPEC",
            )
        ]

    mode = _openapi_source_mode()
    if mode in ("fastapi", "import", "app"):
        if dry_run:
            _emit_openapi_debug(
                "dry-run",
                [
                    "mode=fastapi (PYKOTMIG_OPENAPI_SOURCE) dry_run: skipping import and app.openapi().",
                    f"app_spec={app_spec!r} module={mod_name!r} attr={attr_name!r}",
                ],
                stream=stream,
            )
            return None, []
        return _load_openapi_via_fastapi_import(project_root, app_spec)
    if mode not in ("ollama", "llm", ""):
        errors.append(
            ErrorItem(
                message=f"Unknown PYKOTMIG_OPENAPI_SOURCE={mode!r}; expected ollama or fastapi.",
                hint="Unset the variable for default (ollama), or set PYKOTMIG_OPENAPI_SOURCE=fastapi.",
                rule_id="BAD_OPENAPI_SOURCE",
            )
        )
        return None, errors

    return _ollama_chat_openapi(project_root, app_spec, dry_run=dry_run, debug_stream=debug_stream)
