# Component catalog (PyKotMig)

This catalog lists **MVP components** the project documents with **paired Python (FastAPI) and Kotlin (Ktor)** references. It is **not** a claim of full Python-to-Kotlin automation yet—the [tool](../tool/README.md) is planned; these rows define what “supported” will mean.

Machine-readable manifest: [`manifest.json`](manifest.json).

## Glossary

| Term          | Meaning                                                                     |
|---------------|-----------------------------------------------------------------------------|
| **Component** | A unit we can point to in code (route, model, client, middleware, …).       |
| **Pass**      | Pipeline stage: extract structure → attach metadata → emit Kotlin → verify. |
| **Catalog**   | This list plus `manifest.json`—stable IDs for Phase 2+ tooling.             |
| **Parity**    | Same HTTP contract and JSON shapes between Python and Kotlin demos.         |

## Industry context

Python appears at large companies as HTTP APIs, queue workers, stream jobs, batch pipelines, and more—not every shape is a **Kotlin service migration** target for this repo. A pattern-level map with **Must-hit / Catalog-later / Not-a-target** tags lives in [`docs/plans/2026-05-14-faang-python-services-taxonomy-design.md`](../docs/plans/2026-05-14-faang-python-services-taxonomy-design.md). Rows below marked **MVP** align with **Must-hit**; **v2** rows point toward **Catalog-later**; other archetypes in that doc are narrative scope only unless promoted here later.

## MVP index

Components match the MVP checklist in `.planning/research/RESEARCH-04-scope-portfolio.md`.

| Component                          | MVP    | Tags              | Python reference                                                                                                                                | Kotlin reference                                                                                                                                                                                                                |
|------------------------------------|--------|-------------------|-------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| HTTP routes                        | ✓      | fastapi, portable | [status-hub/app.py](../examples/status-hub/python/src/status_hub/app.py), [order-api/routes](../examples/order-api/python/src/order_api/app.py) | [status-hub/Application.kt](../examples/status-hub/kotlin/src/main/kotlin/dev/pykotmig/statushub/Application.kt), [order-api/Application.kt](../examples/order-api/kotlin/src/main/kotlin/dev/pykotmig/orderapi/Application.kt) |
| JSON models                        | ✓      | fastapi, portable | [status-hub/app.py](../examples/status-hub/python/src/status_hub/app.py) (Pydantic models)                                                      | [status-hub/Application.kt](../examples/status-hub/kotlin/src/main/kotlin/dev/pykotmig/statushub/Application.kt) (`@Serializable`)                                                                                              |
| Validation / 422                   | ✓      | fastapi           | [status-hub/app.py](../examples/status-hub/python/src/status_hub/app.py)                                                                        | [status-hub/Application.kt](../examples/status-hub/kotlin/src/main/kotlin/dev/pykotmig/statushub/Application.kt)                                                                                                                |
| Dependency injection               | ✓      | fastapi           | [order-api/deps.py](../examples/order-api/python/src/order_api/deps.py)                                                                         | [order-api/Koin.kt](../examples/order-api/kotlin/src/main/kotlin/dev/pykotmig/orderapi/Koin.kt)                                                                                                                                 |
| Middleware (logging / correlation) | ✓      | fastapi, portable | [status-hub/app.py](../examples/status-hub/python/src/status_hub/app.py)                                                                        | [status-hub/Application.kt](../examples/status-hub/kotlin/src/main/kotlin/dev/pykotmig/statushub/Application.kt)                                                                                                                |
| Config (env + defaults)            | ✓      | portable          | [order-api/config.py](../examples/order-api/python/src/order_api/config.py)                                                                     | [order-api/Config.kt](../examples/order-api/kotlin/src/main/kotlin/dev/pykotmig/orderapi/Config.kt)                                                                                                                             |
| Structured logging                 | ✓      | portable          | [order-api/logging_conf.py](../examples/order-api/python/src/order_api/logging_conf.py)                                                         | [order-api/Application.kt](../examples/order-api/kotlin/src/main/kotlin/dev/pykotmig/orderapi/Application.kt) (SLF4J)                                                                                                           |
| Outbound HTTP client               | ✓      | portable          | [order-api/notify_client.py](../examples/order-api/python/src/order_api/notify_client.py)                                                       | [order-api/NotifyClient.kt](../examples/order-api/kotlin/src/main/kotlin/dev/pykotmig/orderapi/NotifyClient.kt)                                                                                                                 |
| Health / readiness                 | ✓      | portable          | [status-hub/app.py](../examples/status-hub/python/src/status_hub/app.py) (`GET /health`)                                                        | [status-hub/Application.kt](../examples/status-hub/kotlin/src/main/kotlin/dev/pykotmig/statushub/Application.kt)                                                                                                                |
| Background / async task            | — (v2) | fastapi           | _deferred_                                                                                                                                      | _deferred_                                                                                                                                                                                                                      |
| Auth stub                          | — (v2) | fastapi           | _deferred_                                                                                                                                      | _deferred_                                                                                                                                                                                                                      |

## Demos

| Demo                                           | Purpose                          |
|------------------------------------------------|----------------------------------|
| [Status Hub](../examples/status-hub/README.md) | Minimal routes + echo validation |
| [Order API](../examples/order-api/README.md)   | CRUD + outbound client + DI      |
