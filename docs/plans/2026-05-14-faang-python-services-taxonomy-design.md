# Design: FAANG-scale Python service archetypes + PyKotMig scope tags

**Date:** 2026-05-14  
**Status:** Approved (brainstorming Sections 1–3)

## 1. Purpose, audience, boundaries

**Purpose:** Provide a pattern-level map of Python workloads commonly seen at very large product companies, and tag each archetype for **PyKotMig**: what the migration showcase **must** cover first, what belongs in a **later catalog**, and what is **not a conversion target** for a Kotlin HTTP service story.

**Audience:** Maintainer (portfolio + roadmap) and reviewers asking why the project leads with **FastAPI-shaped HTTP** parity before broader Python ecosystems.

**Boundaries:** Industry patterns only—no company-specific technology claims. This document does not assert tooling coverage beyond what the Phase 1 catalog and roadmap already promise.

## 2. Structure of the map

**Spine:** Workload **topology** (how work enters the system): online request–response, async/queue, stream, scheduled/batch, ML, platform.

**Secondary lens:** A short “layer” label (edge API, worker, data, ML, platform) may be used in prose for readability; topology remains authoritative.

## 3. Archetypes and PyKotMig tags

| Topology | Archetype | PyKotMig tag |
|----------|-----------|--------------|
| Online / request–response | Stateless **JSON HTTP** APIs (CRUD, BFFs, small domain services) | **Must-hit** |
| Online | **Health / readiness / metrics** and structured logging in-process | **Must-hit** |
| Online | **Outbound HTTP** to dependencies (timeouts, retries, correlation) | **Must-hit** |
| Online | **Auth** middleware (JWT/OIDC/API keys), coarse RBAC | **Catalog-later** |
| Online | **WebSocket / SSE** long-lived connections | **Catalog-later** |
| Online | **gRPC** (or other IDL) services with Python handlers | **Catalog-later** |
| Online | **Server-rendered** web (e.g. template-heavy stacks) | **Catalog-later** (different surface than JSON-first; may stay narrative-only unless scope expands) |
| Async / queue | **Queue workers** (managed queues, buses), idempotent handlers | **Catalog-later** |
| Async | **In-process background** work and side effects | **Catalog-later** |
| Stream | **Stream consumers** (Kafka/Kinesis-style), windows, replay | **Not-a-target** |
| Scheduled | **Cron / scheduler** jobs, workflow engines’ Python task bodies | **Not-a-target** |
| Batch | **ETL / PySpark** drivers and large dataframe jobs | **Not-a-target** |
| ML | **Inference** behind HTTP (thin API + heavier runtime) | **Must-hit** for **HTTP + schema** at the boundary; **Catalog-later** for model load/GPU lifecycle as first-class components |
| ML | **Training**, notebooks, experiment glue | **Not-a-target** |
| Platform | **CLIs**, one-off scripts, local-only tools | **Not-a-target** |
| Platform | **Serverless**-style handlers (packaging and cold-start story differ) | **Catalog-later** |

**Interpretation of “FAANG scale”:** Many teams ship these **shapes**; high-QPS paths are often **not** Python-exclusive. Python remains common for **data-adjacent APIs**, **glue**, **ML boundaries**, and **internal tools**.

## 4. Cross-cutting concerns by tag

### Must-hit (HTTP-first service)

- **Observability:** Request logging, correlation IDs, health/readiness, basic metrics hooks—**parity targets** between Python and Kotlin reference examples (middleware, structured logging, `/health`).
- **Errors:** Stable HTTP status codes and **machine-readable** bodies (e.g. validation 422 shape, domain 4xx/5xx conventions)—treat as **contract** inputs for OpenAPI and golden HTTP checks later.
- **Idempotency:** Document where it matters for HTTP (safe GET retries). Idempotency keys on mutating POST as a **Catalog-later** narrative, not an MVP requirement.
- **Testing:** Contract-level verification (OpenAPI diff, golden HTTP) as the **verification ladder** spine; unit tests where they directly support the demos.

### Catalog-later

- **Observability:** Consumer lag, stream offsets, gRPC interceptors—**future catalog** items, not Phase 1 parity claims.
- **Errors:** Poison messages, partial batch failure, broker retry policies—**appendix** patterns only.
- **Idempotency:** At-least-once delivery and dedupe—**migration story TBD** in tooling.
- **Testing:** Broker-backed or gRPC integration tests—**outside MVP CI** unless dedicated infra is added.

### Not-a-target

- **Observability, errors, idempotency, testing:** Brief rationale each: different runtime, different deployable unit, or not a long-lived “service” in the PyKotMig sense. No component-table commitment.

### Data flow summary

- **Must-hit:** Client → HTTP → handler → (optional) outbound HTTP → response.
- **Catalog-later:** Adds broker/stream or additional protocols around the same business logic where applicable.
- **Not-a-target:** Batch/Spark/training/notebook paths—out of scope for the Kotlin HTTP migration thesis.

## 5. Alignment with PyKotMig today

Phase 1 catalog emphasis (**routes, models, validation, DI, middleware, config, logging, outbound client, health**) matches the **Must-hit** row set. Items already marked **v2** in the catalog (**background tasks**, **auth stub**) align with **Catalog-later** above.

---

*Brainstorming workflow: Sections 1–3 approved in chat on 2026-05-14.*
