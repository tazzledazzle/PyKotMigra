from __future__ import annotations

import ast
import hashlib
from pathlib import Path

from pykotmig.ir import ErrorItem, FileRecord

SKIP_DIR_NAMES = frozenset(
    {
        ".venv",
        "__pycache__",
        ".git",
        ".pytest_cache",
        ".mypy_cache",
        "node_modules",
        ".pykotmig",
        ".tox",
        "dist",
        "build",
    }
)


def _skip_path(path: Path) -> bool:
    return any(part in SKIP_DIR_NAMES for part in path.parts)


def discover_py_files(project_root: Path) -> list[Path]:
    """Return sorted *.py paths under project_root/src (excluding skip dirs)."""
    src = project_root / "src"
    if not src.is_dir():
        return []
    out: list[Path] = []
    for p in src.rglob("*.py"):
        if _skip_path(p.relative_to(src)):
            continue
        out.append(p)
    return sorted(out, key=lambda x: x.as_posix())


def extract_imports(tree: ast.Module) -> list[str]:
    names: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if node.names:
                for alias in node.names:
                    if alias.name == "*":
                        names.append(f"{mod}.*")
                    else:
                        names.append(f"{mod}.{alias.name}" if mod else alias.name)
            elif mod:
                names.append(mod)
    return sorted(set(names))


def analyze_python_source(
    rel_path: str,
    source: str,
) -> tuple[FileRecord | None, ErrorItem | None]:
    """Parse source; return FileRecord or None + optional fatal-style ErrorItem."""
    raw = source.encode("utf-8")
    digest = hashlib.sha256(raw).hexdigest()
    size = len(raw)
    try:
        tree = ast.parse(source, filename=rel_path)
    except SyntaxError as e:
        err = ErrorItem(
            path=rel_path,
            message=str(e),
            hint="Fix syntax before LibCST or OpenAPI extraction can run on this file.",
            rule_id="PY_SYNTAX",
        )
        rec = FileRecord(
            path=rel_path,
            sha256=digest,
            bytes=size,
            ast_ok=False,
            ast_error=f"{e.msg} (line {e.lineno})",
            imports=[],
            libcst_ok=False,
        )
        return rec, err
    imports = extract_imports(tree)
    return (
        FileRecord(
            path=rel_path,
            sha256=digest,
            bytes=size,
            ast_ok=True,
            ast_error=None,
            imports=imports,
            libcst_ok=False,
        ),
        None,
    )


def try_libcst(rel_path: str, source: str) -> tuple[bool, str | None]:
    import libcst as cst

    try:
        cst.parse_module(source)
        return True, None
    except Exception as e:  # libcst raises various parse errors
        return False, f"{type(e).__name__}: {e}"
