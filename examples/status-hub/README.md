# Status Hub (reference demo)

**Small** demo: health, version metadata, validated JSON echo, **catalog v2** samples (`POST /jobs` deferred work, `GET /secure/ping` with `x-api-key`). Intended for the fastest Python ↔ Kotlin contract comparison.

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

## Contract baseline (Phase 4)

- **OpenAPI:** [`contracts/openapi.json`](contracts/openapi.json) is regenerated from the FastAPI app. Python tests fail if it drifts.
- **Golden HTTP:** Kotlin tests in `kotlin/` mirror the same JSON response bodies for `/health`, `/version`, successful `/echo`, `/secure/ping` (200 + 401), and `POST /jobs` (202 + background completion).

## Environment

| Variable | Meaning |
|----------|---------|
| `STATUS_HUB_API_KEY` | Expected value for `x-api-key` on `/secure/ping` (default **demo-key**). |

Regenerate OpenAPI from `python/`:

```bash
uv run python ../../scripts/export_openapi.py status-hub
```

See the [root README](../../README.md) for full quickstart.