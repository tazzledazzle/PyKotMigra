"""Edge cases for OpenAPI → Kotlin emission."""

from __future__ import annotations

import pytest

from pykotmig.codegen.load import CodegenError
from pykotmig.codegen.openapi_kotlin import (
    _default_literal_for_schema,
    _kotlin_ident,
    _schema_to_kotlin_type,
    emit_models_kotlin,
)


def test_kotlin_ident_reserved_word() -> None:
    assert _kotlin_ident("class") == "`class`"
    assert _kotlin_ident("message") == "message"


def test_schema_ref_and_primitives() -> None:
    schemas = {"Item": {"type": "object", "properties": {"id": {"type": "integer"}}}}
    assert _schema_to_kotlin_type({"$ref": "#/components/schemas/Item"}, schemas) == "Item"
    assert _schema_to_kotlin_type({"type": "string"}, schemas) == "String"
    assert _schema_to_kotlin_type({"type": "number"}, schemas) == "Double"
    assert _schema_to_kotlin_type({"type": "boolean"}, schemas) == "Boolean"
    assert _schema_to_kotlin_type({"type": "array", "items": {"type": "string"}}, schemas) == "List<String>"


def test_schema_unsupported_ref() -> None:
    with pytest.raises(CodegenError) as exc:
        _schema_to_kotlin_type({"$ref": "http://other/Item"}, {})
    assert exc.value.rule_id == "GEN_OPENAPI_UNSUPPORTED"


def test_schema_inline_object_rejected() -> None:
    with pytest.raises(CodegenError):
        _schema_to_kotlin_type({"type": "object"}, {})


def test_schema_depth_guard() -> None:
    deep = {"type": "array", "items": {"type": "array", "items": {"type": "string"}}}
    for _ in range(20):
        deep = {"type": "array", "items": deep}
    with pytest.raises(CodegenError):
        _schema_to_kotlin_type(deep, {}, _depth=12)


def test_default_literals() -> None:
    schemas: dict = {}
    assert _default_literal_for_schema({"type": "string", "default": "hi"}, schemas) == '"hi"'
    assert _default_literal_for_schema({"type": "integer", "default": 3}, schemas) == "3"
    assert _default_literal_for_schema({"type": "number", "default": 1.5}, schemas) == "1.5"
    assert _default_literal_for_schema({"type": "boolean", "default": False}, schemas) == "false"


def test_emit_models_skips_non_object_schemas() -> None:
    openapi = {
        "components": {
            "schemas": {
                "HTTPValidationError": {"type": "object"},
                "Tag": {"type": "string"},
                "EmptyObj": {"type": "object", "properties": {}},
            }
        }
    }
    src = emit_models_kotlin(openapi, "dev.test")
    assert "data class" not in src
    assert "package dev.test" in src
