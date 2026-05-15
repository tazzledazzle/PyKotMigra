# Order API (reference demo)

**Medium** demo: in-memory order CRUD plus one **outbound HTTP notification** call to a configurable URL.

## Layout

- `python/` — FastAPI + `httpx` (`uv` + `pytest`; outbound mocked in tests)
- `kotlin/` — Ktor + Ktor Client + Koin (`./gradlew test` / `./gradlew run`)

## Environment

| Variable | Meaning |
|----------|---------|
| `EXTERNAL_HTTP_URL` | Optional base URL (e.g. `http://127.0.0.1:9999`). If unset or empty, outbound notify is **skipped** (logged) so local runs never hang. |
| `PORT` | Listen port (default **8081** Python / Kotlin). |

## Run

**Python** (from `python/`):

```bash
uv sync
uv run uvicorn order_api.app:app --host 127.0.0.1 --port 8081
```

**Kotlin** (from `kotlin/`):

```bash
./gradlew run
```

## Contract baseline (Phase 4)

- **OpenAPI:** [`contracts/openapi.json`](contracts/openapi.json) is regenerated from the FastAPI app; `tests/test_openapi_contract.py` fails on drift.
- **Golden HTTP:** Kotlin tests assert the same JSON bodies as Python for CRUD, 404, and invalid title (422).
- **Notify client:** Kotlin `HttpClient` uses **2s** connect + request timeouts (matches Python `httpx.Client(timeout=2.0)`).

Regenerate OpenAPI from `python/`:

```bash
uv run python ../../scripts/export_openapi.py order-api
```

See the [root README](../../README.md) for full quickstart.
