"""LangChain Runnable batch and edge inputs."""

from __future__ import annotations

from ai_pipeline_demo.chain import build_demo_pipeline


def test_batch_invoke_multiple_queries() -> None:
    chain = build_demo_pipeline()
    out = chain.batch([{"query": "  a  "}, {"query": "b"}])
    assert len(out) == 2
    assert "a" in out[0]["answer"]
    assert "b" in out[1]["answer"]


def test_empty_query_still_runs() -> None:
    chain = build_demo_pipeline()
    r = chain.invoke({"query": ""})
    assert "sources=2" in r["answer"]
