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

See the [root README](../../README.md) for full quickstart.
