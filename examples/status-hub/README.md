# Status Hub (reference demo)

**Small** demo: health, version metadata, and a validated JSON echo. Intended for the fastest Python ↔ Kotlin contract comparison.

## Layout

- `python/` — FastAPI + Pydantic v2 (`uv` + `pytest`)
- `kotlin/` — Ktor + kotlinx.serialization (`./gradlew test` / `./gradlew run`)

## Run

**Python** (from `python/`):

```bash
uv sync
uv run uvicorn status_hub.app:app --host 127.0.0.1 --port 8080
```

**Kotlin** (from `kotlin/`):

```bash
./gradlew run
```

Default listen address is **127.0.0.1**; port **8080** unless overridden by `PORT`.

See the [root README](../../README.md) for full quickstart.
