from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CliInfo(BaseModel):
    version: str
    argv: list[str] = Field(default_factory=list)


class ErrorItem(BaseModel):
    path: str | None = None
    message: str
    hint: str = ""
    rule_id: str = "unknown"


class GapItem(BaseModel):
    path: str
    message: str
    code: str = ""


class ImportEdge(BaseModel):
    src: str
    dst: str
    kind: str = "import"


class FileRecord(BaseModel):
    path: str
    sha256: str
    bytes: int
    ast_ok: bool
    ast_error: str | None = None
    imports: list[str] = Field(default_factory=list)
    libcst_ok: bool = False
    libcst_error: str | None = None


class MypySummary(BaseModel):
    attempted: bool = False
    exit_code: int | None = None
    stdout: str = ""
    stderr: str = ""
    hint: str | None = None


class AnalysisRoot(BaseModel):
    schema_version: int = 1
    generated_at: str
    project_root: str
    cli: CliInfo
    files: list[FileRecord] = Field(default_factory=list)
    import_graph: list[ImportEdge] = Field(default_factory=list)
    openapi: dict[str, Any] | None = None
    gaps: list[GapItem] = Field(default_factory=list)
    errors: list[ErrorItem] = Field(default_factory=list)
    mypy: MypySummary | None = None
