from __future__ import annotations

import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pykotmig import __version__
from pykotmig.cache import get_cached_record, load_file_state, put_cached_record, save_file_state
from pykotmig.ir import AnalysisRoot, CliInfo, ErrorItem, FileRecord, GapItem, ImportEdge, MypySummary
from pykotmig.openapi_load import load_openapi_dict
from pykotmig.scan import analyze_python_source, discover_py_files, try_libcst


def _build_import_graph(files: list[FileRecord]) -> list[ImportEdge]:
    edges: list[ImportEdge] = []
    for f in files:
        if not f.ast_ok:
            continue
        for imp in f.imports:
            edges.append(ImportEdge(src=f.path, dst=imp, kind="import"))
    return edges


def _run_mypy(project_root: Path) -> MypySummary:
    import subprocess

    try:
        r = subprocess.run(
            ["mypy", "src", "--show-error-codes", "--no-error-summary"],
            cwd=str(project_root.resolve()),
            capture_output=True,
            text=True,
            timeout=180,
        )
        return MypySummary(
            attempted=True,
            exit_code=r.returncode,
            stdout=(r.stdout or "") + (r.stderr or ""),
            stderr="",
        )
    except FileNotFoundError:
        return MypySummary(
            attempted=True,
            hint="mypy not found on PATH; install mypy in the active environment or omit --mypy.",
        )
    except Exception as e:  # noqa: BLE001
        return MypySummary(attempted=True, hint=f"mypy failed to start: {e}")


def run_analyze(
    project_root: Path,
    app_spec: str,
    *,
    force: bool = False,
    mypy_enable: bool = False,
    argv: list[str] | None = None,
    dry_run: bool = False,
) -> AnalysisRoot:
    root = project_root.resolve()
    state: dict[str, Any] = {} if force or dry_run else load_file_state(root)

    files_out: list[FileRecord] = []
    errors: list[ErrorItem] = []
    gaps: list[GapItem] = []

    for path in discover_py_files(root):
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()

        cached = None if force else get_cached_record(state, rel, digest)
        if cached is not None:
            files_out.append(FileRecord.model_validate(cached))
            continue

        rec, syn_err = analyze_python_source(rel, text)
        if syn_err is not None:
            errors.append(syn_err)

        assert rec is not None
        if rec.ast_ok:
            ok, err = try_libcst(rel, text)
            rec = rec.model_copy(update={"libcst_ok": ok, "libcst_error": err})
            if not ok and err:
                gaps.append(GapItem(path=rel, message=err, code="LIBCST_PARSE"))

        files_out.append(rec)
        if not dry_run:
            put_cached_record(state, rel, digest, rec.model_dump(mode="json"))

    if not dry_run:
        save_file_state(root, state)

    openapi, oerrs = load_openapi_dict(root, app_spec, dry_run=dry_run)
    errors.extend(oerrs)

    mypy_result: MypySummary | None = None
    if mypy_enable:
        mypy_result = _run_mypy(root)

    files_sorted = sorted(files_out, key=lambda f: f.path)
    return AnalysisRoot(
        schema_version=1,
        generated_at=datetime.now(timezone.utc).isoformat(),
        project_root=str(root),
        cli=CliInfo(version=__version__, argv=list(argv or sys.argv)),
        files=files_sorted,
        import_graph=_build_import_graph(files_sorted),
        openapi=openapi,
        gaps=gaps,
        errors=errors,
        mypy=mypy_result,
    )
