"""Composable Runnable pipeline (RAG/agent mental model, no network)."""

from __future__ import annotations

from typing import Any

from langchain_core.runnables import RunnableLambda


def _normalize_query(data: dict[str, Any]) -> dict[str, Any]:
    q = str(data.get("query", "")).strip()
    return {"query": q}


def _build_context(data: dict[str, Any]) -> dict[str, Any]:
    """Fake retriever: attach static context lines."""
    ctx = ["doc:overview", "doc:faq"]
    return {**data, "context": ctx}


def _render_answer(data: dict[str, Any]) -> dict[str, Any]:
    q = data["query"]
    ctx = data.get("context", [])
    return {"answer": f"q={q!r} sources={len(ctx)}"}


def build_demo_pipeline() -> Any:
    """Return a linear chain: normalize → retrieve → render."""
    return (
        RunnableLambda(_normalize_query)
        | RunnableLambda(_build_context)
        | RunnableLambda(_render_answer)
    )
