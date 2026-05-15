from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pykotmig.ir import AnalysisRoot


@dataclass
class CodegenError(Exception):
    message: str
    hint: str = ""
    rule_id: str = "GEN_INPUT"

    def __str__(self) -> str:  # pragma: no cover - surfaced to CLI
        h = f" ({self.hint})" if self.hint else ""
        return f"[{self.rule_id}] {self.message}{h}"


def load_analysis(path: Path) -> AnalysisRoot:
    raw = path.read_text(encoding="utf-8")
    return AnalysisRoot.model_validate_json(raw)


def assert_ready_for_codegen(
    root: AnalysisRoot,
    *,
    allow_errors: bool = False,
) -> None:
    if root.openapi is None:
        raise CodegenError(
            "analysis.json has no openapi section (run analyze with a valid --app).",
            hint="Ensure FastAPI app loads and `app.openapi()` succeeds.",
            rule_id="GEN_NO_OPENAPI",
        )
    if root.errors and not allow_errors:
        first = root.errors[0]
        raise CodegenError(
            f"analysis.json contains {len(root.errors)} error(s); first: {first.message}",
            hint=first.hint or "Fix analyzer errors or pass --allow-errors (unsafe).",
            rule_id="GEN_ANALYSIS_ERRORS",
        )
