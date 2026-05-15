from __future__ import annotations

from pathlib import Path

from pykotmig.scan import analyze_python_source, discover_py_files


def _write_layout(root: Path) -> None:
    (root / "pyproject.toml").write_text('[project]\nname="t"\nversion="0"\n', encoding="utf-8")
    (root / "src/pkg").mkdir(parents=True)
    (root / "src/pkg/ok.py").write_text("import os\nfrom typing import Any\n\nX = 1\n", encoding="utf-8")
    (root / "src/pkg/bad.py").write_text("def x(\n", encoding="utf-8")
    v = root / "src" / ".venv"
    v.mkdir(parents=True, exist_ok=True)
    (v / "ignore.py").write_text("IGNORE=1\n", encoding="utf-8")


def test_discover_skips_venv(tmp_path: Path) -> None:
    _write_layout(tmp_path)
    paths = discover_py_files(tmp_path)
    rels = [p.relative_to(tmp_path).as_posix() for p in paths]
    assert "src/pkg/ok.py" in rels
    assert not any(".venv" in r for r in rels)


def test_syntax_error_recorded(tmp_path: Path) -> None:
    _write_layout(tmp_path)
    text = (tmp_path / "src/pkg/bad.py").read_text()
    rec, err = analyze_python_source("src/pkg/bad.py", text)
    assert rec is not None
    assert rec.ast_ok is False
    assert err is not None
    assert err.rule_id == "PY_SYNTAX"


def test_imports_extracted(tmp_path: Path) -> None:
    _write_layout(tmp_path)
    text = (tmp_path / "src/pkg/ok.py").read_text()
    rec, err = analyze_python_source("src/pkg/ok.py", text)
    assert err is None
    assert rec is not None
    assert rec.ast_ok is True
    assert "os" in rec.imports
    assert any("typing" in i for i in rec.imports)
