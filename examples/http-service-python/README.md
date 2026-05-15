# HTTP service (Python)

**Map:** FastAPI / Flask-style HTTP APIs → **Ktor** (`ktor-server-core`, `ktor-server-netty`).

## Layout

- `python/` — FastAPI (`uv` + `pytest`)
- `kotlin/` — Ktor + Netty (`./gradlew test` / `./gradlew run`)

## Python

```bash
cd python && uv sync && uv run uvicorn http_service_demo.app:app --reload --port 8010
uv run pytest -q && uv run mypy src && uv run ruff check src tests
```

See `python/src/http_service_demo/app.py`.

## Kotlin

```bash
cd kotlin && ./gradlew test && ./gradlew run
```

Listen port defaults to **8010**; override with `PORT`. Endpoints: `GET /health`, `POST /greet`.
