# Catalog showcase (Python)

Minimal **FastAPI** service laid out as **one module per row** in [`../../catalog/README.md`](../../catalog/README.md). Use these files as stable pointers for tooling and docs; **Status Hub** and **Order API** remain the primary paired Kotlin references for MVP rows until Ktor parity exists here.

Run:

```bash
uv sync
uv run uvicorn catalog_showcase.app:app --reload --port 8090
```

Tests:

```bash
uv sync --extra dev
uv run pytest -q
```

| Catalog component       | Module                                                                                 |
|-------------------------|----------------------------------------------------------------------------------------|
| HTTP routes             | [`src/catalog_showcase/routes.py`](src/catalog_showcase/routes.py)                     |
| JSON models             | [`src/catalog_showcase/models.py`](src/catalog_showcase/models.py)                     |
| Validation / 422        | [`src/catalog_showcase/validation.py`](src/catalog_showcase/validation.py)             |
| Dependency injection    | [`src/catalog_showcase/deps.py`](src/catalog_showcase/deps.py)                         |
| Middleware              | [`src/catalog_showcase/middleware.py`](src/catalog_showcase/middleware.py)             |
| Config                  | [`src/catalog_showcase/config.py`](src/catalog_showcase/config.py)                     |
| Structured logging      | [`src/catalog_showcase/logging_conf.py`](src/catalog_showcase/logging_conf.py)         |
| Outbound HTTP client    | [`src/catalog_showcase/outbound_client.py`](src/catalog_showcase/outbound_client.py)   |
| Health / readiness      | [`src/catalog_showcase/health.py`](src/catalog_showcase/health.py)                     |
| Background / async task | [`src/catalog_showcase/background_tasks.py`](src/catalog_showcase/background_tasks.py) |
| Auth stub               | [`src/catalog_showcase/auth_stub.py`](src/catalog_showcase/auth_stub.py)               |
| App assembly            | [`src/catalog_showcase/app.py`](src/catalog_showcase/app.py)                           |
