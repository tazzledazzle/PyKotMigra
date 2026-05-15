# Async task worker (Python)

**Map:** Temporal / Celery-style workers → **Temporal Java SDK** in Kotlin (`temporal-sdk`, `io.temporal.*`).

This repo ships a **stdlib-only asyncio** job queue + worker pool that mirrors *process jobs from a queue with concurrency* without pulling the full Temporal/Celery stack into CI.

## Layout

- `python/` — asyncio queue + worker pool (`uv` + `pytest`)
- `kotlin/` — `kotlinx.coroutines` channel pool mirroring the Python tests (`./gradlew test`)

## Python

```bash
cd python && uv sync --extra dev && uv run pytest -q && uv run mypy src
```

## Kotlin

```bash
cd kotlin && ./gradlew test
```

Includes a **Temporal** in-memory workflow smoke test (`TemporalSmokeTest`) alongside the asyncio-style `runPool` mirror.
