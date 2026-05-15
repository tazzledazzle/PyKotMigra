# AI pipeline (Python)

**Map:** LangChain-style agents → **LangChain4j** in Kotlin (`langchain4j-core`, provider modules).

This demo uses **`langchain-core`** only: a small `Runnable` pipeline with no live LLM call in tests.

## Layout

- `python/` — linear Runnable-style chain (`uv` + `pytest`)
- `kotlin/` — same normalize → retrieve → render flow in plain Kotlin (`./gradlew test`)

## Python

```bash
cd python && uv sync --extra dev && uv run pytest -q && uv run mypy src
```

## Kotlin

```bash
cd kotlin && ./gradlew test
```

Uses **LangChain4j** `Document` for the fake “retriever” step while keeping the pipeline deterministic (no live LLM calls in CI).
