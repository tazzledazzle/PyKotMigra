# Component catalog (PyKotMig)

This catalog lists **MVP components** the project documents with **paired Python (FastAPI) and Kotlin (Ktor)** references. It is **not** a claim of full Python-to-Kotlin automation yet—the [tool](../tool/README.md) is planned; these rows define what “supported” will mean.

Machine-readable manifest: [`manifest.json`](manifest.json).

## Glossary

| Term          | Meaning                                                                     |
|---------------|-----------------------------------------------------------------------------|
| **Component** | A unit we can point to in code (route, model, client, middleware, …).       |
| **Pass**      | Pipeline stage: extract structure → attach metadata → emit Kotlin → verify. |
| **Catalog**   | This list plus `manifest.json`—stable IDs for Phase 2+ tooling.             |
| **Parity**    | For Status Hub + Order API: committed **OpenAPI** (`contracts/openapi.json`) matches FastAPI; **golden HTTP** tests keep success-path JSON bodies aligned between Python and Kotlin (CI: `reference-demos-parity` job). |

## Industry context

Python appears at large companies as HTTP APIs, queue workers, stream jobs, batch pipelines, and more—not every shape is a **Kotlin service migration** target for this repo. A pattern-level map with **Must-hit / Catalog-later / Not-a-target** tags lives in [`docs/plans/2026-05-14-faang-python-services-taxonomy-design.md`](../docs/plans/2026-05-14-faang-python-services-taxonomy-design.md). Rows below marked **MVP** align with **Must-hit**; **v2** rows point toward **Catalog-later**; other archetypes in that doc are narrative scope only unless promoted here later.

## MVP index

Components match the MVP checklist in `.planning/research/RESEARCH-04-scope-portfolio.md`.

Primary **Python** pointers use the [**catalog-showcase**](../examples/catalog-showcase/python/README.md) modules (one file per row). **Kotlin** pointers remain the original paired demos unless noted.

| Component                          | MVP    | Tags              | Python reference                                                                                                                                 | Kotlin reference                                                                                                                                                                                                                |
|------------------------------------|--------|-------------------|---------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| HTTP routes                        | ✓      | fastapi, portable | [routes.py](../examples/catalog-showcase/python/src/catalog_showcase/routes.py) · [status-hub/app.py](../examples/status-hub/python/src/status_hub/app.py), [order-api/app.py](../examples/order-api/python/src/order_api/app.py) | [status-hub/Application.kt](../examples/status-hub/kotlin/src/main/kotlin/dev/pykotmig/statushub/Application.kt), [order-api/Application.kt](../examples/order-api/kotlin/src/main/kotlin/dev/pykotmig/orderapi/Application.kt) |
| JSON models                        | ✓      | fastapi, portable | [models.py](../examples/catalog-showcase/python/src/catalog_showcase/models.py) · [status-hub/app.py](../examples/status-hub/python/src/status_hub/app.py)                                                      | [status-hub/Application.kt](../examples/status-hub/kotlin/src/main/kotlin/dev/pykotmig/statushub/Application.kt) (`@Serializable`)                                                                                              |
| Validation / 422                   | ✓      | fastapi           | [validation.py](../examples/catalog-showcase/python/src/catalog_showcase/validation.py) · [status-hub/app.py](../examples/status-hub/python/src/status_hub/app.py)                                                | [status-hub/Application.kt](../examples/status-hub/kotlin/src/main/kotlin/dev/pykotmig/statushub/Application.kt)                                                                                                                |
| Dependency injection               | ✓      | fastapi           | [deps.py](../examples/catalog-showcase/python/src/catalog_showcase/deps.py) · [order-api/deps.py](../examples/order-api/python/src/order_api/deps.py)                                                           | [order-api/Koin.kt](../examples/order-api/kotlin/src/main/kotlin/dev/pykotmig/orderapi/Koin.kt)                                                                                                                                 |
| Middleware (logging / correlation) | ✓      | fastapi, portable | [middleware.py](../examples/catalog-showcase/python/src/catalog_showcase/middleware.py) · [status-hub/app.py](../examples/status-hub/python/src/status_hub/app.py)                                                | [status-hub/Application.kt](../examples/status-hub/kotlin/src/main/kotlin/dev/pykotmig/statushub/Application.kt)                                                                                                                |
| Config (env + defaults)            | ✓      | portable          | [config.py](../examples/catalog-showcase/python/src/catalog_showcase/config.py) · [order-api/config.py](../examples/order-api/python/src/order_api/config.py)                                                    | [order-api/Config.kt](../examples/order-api/kotlin/src/main/kotlin/dev/pykotmig/orderapi/Config.kt)                                                                                                                             |
| Structured logging                 | ✓      | portable          | [logging_conf.py](../examples/catalog-showcase/python/src/catalog_showcase/logging_conf.py) · [order-api/logging_conf.py](../examples/order-api/python/src/order_api/logging_conf.py)                             | [order-api/Application.kt](../examples/order-api/kotlin/src/main/kotlin/dev/pykotmig/orderapi/Application.kt) (SLF4J)                                                                                                           |
| Outbound HTTP client               | ✓      | portable          | [outbound_client.py](../examples/catalog-showcase/python/src/catalog_showcase/outbound_client.py) · [order-api/notify_client.py](../examples/order-api/python/src/order_api/notify_client.py)                     | [order-api/NotifyClient.kt](../examples/order-api/kotlin/src/main/kotlin/dev/pykotmig/orderapi/NotifyClient.kt)                                                                                                                 |
| Health / readiness                 | ✓      | portable          | [health.py](../examples/catalog-showcase/python/src/catalog_showcase/health.py) · [status-hub/app.py](../examples/status-hub/python/src/status_hub/app.py) (`GET /health`)                                        | [status-hub/Application.kt](../examples/status-hub/kotlin/src/main/kotlin/dev/pykotmig/statushub/Application.kt)                                                                                                              |
| Background / async task            | — (v2) | fastapi           | [background_tasks.py](../examples/catalog-showcase/python/src/catalog_showcase/background_tasks.py) · [status-hub/app.py](../examples/status-hub/python/src/status_hub/app.py) (`POST /jobs`)                    | [status-hub/Application.kt](../examples/status-hub/kotlin/src/main/kotlin/dev/pykotmig/statushub/Application.kt) (`POST /jobs`, coroutine `delay`)                                                                            |
| Auth stub                          | — (v2) | fastapi           | [auth_stub.py](../examples/catalog-showcase/python/src/catalog_showcase/auth_stub.py) · [status-hub/app.py](../examples/status-hub/python/src/status_hub/app.py) (`GET /secure/ping`)                            | [status-hub/Application.kt](../examples/status-hub/kotlin/src/main/kotlin/dev/pykotmig/statushub/Application.kt) (`GET /secure/ping`, `x-api-key`)                                                                              |

## Demos

| Demo                                                         | Purpose                                      |
|--------------------------------------------------------------|----------------------------------------------|
| [Status Hub](../examples/status-hub/README.md)               | Minimal routes + echo validation             |
| [Order API](../examples/order-api/README.md)                | CRUD + outbound client + DI                  |
| [Catalog showcase](../examples/catalog-showcase/README.md)   | One **Python** module per catalog component  |
