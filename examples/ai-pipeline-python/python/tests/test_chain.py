import pytest
from ai_pipeline_demo.chain import build_demo_pipeline


@pytest.fixture(scope="module")
def pipeline():
    """Build once per test module — chain construction may be expensive."""
    return build_demo_pipeline()


def test_pipeline_returns_answer_key(pipeline):
    out = pipeline.invoke({"query": "hello world"})
    assert "answer" in out, f"Expected 'answer' key in output, got: {out.keys()}"


def test_pipeline_echoes_query(pipeline):
    query = "hello world"
    out = pipeline.invoke({"query": query})
    answer = out["answer"]
    assert query in answer, (
        f"Expected query {query!r} to appear in answer, got: {answer!r}"
    )


def test_pipeline_strips_whitespace(pipeline):
    """Verify padded input is normalized — matches the original test's intent."""
    out = pipeline.invoke({"query": "  hello world  "})
    answer = out["answer"]
    assert "hello world" in answer, (
        f"Expected stripped query in answer, got: {answer!r}"
    )