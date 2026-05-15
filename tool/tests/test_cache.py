from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pykotmig.analyze as analyze_mod


def _mini_fastapi_project(root: Path) -> None:
    (root / "pyproject.toml").write_text('[project]\nname="mini"\nversion="0"\n', encoding="utf-8")
    (root / "src/mini").mkdir(parents=True)
    (root / "src/mini/app.py").write_text(
        "from fastapi import FastAPI\n"
        "app = FastAPI()\n"
        "@app.get('/')\n"
        "def root():\n"
        "    return {'ok': True}\n",
        encoding="utf-8",
    )


def test_incremental_skips_reparse(tmp_path: Path) -> None:
    _mini_fastapi_project(tmp_path)
    with patch.object(analyze_mod, "analyze_python_source", wraps=analyze_mod.analyze_python_source) as spy:
        analyze_mod.run_analyze(tmp_path, "mini.app:app", force=True)
        first = spy.call_count
    assert first >= 1
    with patch.object(analyze_mod, "analyze_python_source", wraps=analyze_mod.analyze_python_source) as spy:
        analyze_mod.run_analyze(tmp_path, "mini.app:app", force=False)
        second = spy.call_count
    assert second == 0
