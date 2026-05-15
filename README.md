# PyKotMig

**PyKotMig** is a **portfolio** project: a migration toolkit that moves **FastAPI + Pydantic** services toward **Kotlin (Ktor)** using a multi-pass pipeline (scan → attribute → generate → verify). The repo ships a **hand-authored catalog**, **paired reference demos**, a Python **`analyze`** CLI that emits **`analysis.json`**, and a **`generate`** path that emits a **building Ktor + Gradle** tree from that file (Phase 3). Contract parity automation is **Phase 4**.

## MVP scope

- **In scope:** Reference implementations for common service components (HTTP, JSON models, validation, DI, logging, config, outbound HTTP, health). See the [component catalog](catalog/README.md).
- **Out of scope:** Arbitrary Python, Django ORM-heavy apps, metaprogramming, C extensions, “full PyPI” coverage. Unsupported patterns surface as analyzer or codegen errors ([tool](tool/README.md)).

## Prerequisites

- **Python** 3.12+ and [uv](https://docs.astral.sh/uv/)
- **JDK** 17+ and a network fetch for Gradle (first `./gradlew` run downloads the distribution)

## Quickstart

### Status Hub (small demo)

**Python** — from `examples/status-hub/python/`:

```bash
uv sync --extra dev
uv run pytest
uv run uvicorn status_hub.app:app --host 127.0.0.1 --port 8080
```

**Kotlin** — from `examples/status-hub/kotlin/`:

```bash
./gradlew test
./gradlew run
```

### Order API (medium demo)

**Python** — from `examples/order-api/python/`:

```bash
uv sync --extra dev
uv run pytest
uv run uvicorn order_api.app:app --host 127.0.0.1 --port 8081
```

Optional outbound notify on create: set `EXTERNAL_HTTP_URL` (e.g. `http://127.0.0.1:9999`); if unset, notify is skipped.

**Kotlin** — from `examples/order-api/kotlin/`:

```bash
./gradlew test
./gradlew run
```

Same `EXTERNAL_HTTP_URL` behavior as Python.

## Analyze + generate (Phases 2–3)

From the **`pykotmig/` project directory** (the folder that contains `tool/` and `examples/`):

**1. Scan Python → `analysis.json`**

```bash
uv run --directory tool pykotmig-cli analyze \
  --project-root examples/order-api/python \
  --app order_api.app:app \
  --out examples/order-api/python/analysis.json
```

By default, OpenAPI is inferred via **local Ollama** (`POST /api/chat` on `OLLAMA_HOST`, bundled `src/**/*.py`). Set **`PYKOTMIG_OPENAPI_SOURCE=fastapi`** to use `app.openapi()` from an imported FastAPI instance instead (see [tool/README.md](tool/README.md)). Use **`analyze --dry-run`** to print analysis JSON without writing `--out`, and to print Ollama request debug to stderr without calling Ollama.

**2. Emit Kotlin (Ktor + Gradle) from that file**

```bash
rm -rf /tmp/pykotmig-gen-order
uv run --directory tool pykotmig-cli generate \
  --analysis examples/order-api/python/analysis.json \
  --out /tmp/pykotmig-gen-order \
  --kotlin-package dev.pykotmig.gen.orderapi \
  --project-name gen-order-api \
  --profile order-api \
  --force
cd /tmp/pykotmig-gen-order && bash ./gradlew test
```

Use `--profile status-hub` with an analysis produced from `examples/status-hub/python` and `status_hub.app:app`.

Details, flags, and security notes: [tool/README.md](tool/README.md). The script is **`pykotmig-cli`** so it does not clash with the `pykotmig` Python package when using `uv run`.

## Migration passes (planned tool)

1. **Scan** — walk the Python service tree and extract components (routes, models, clients, …).  
2. **Attribute** — attach types and metadata (OpenAPI, static analysis).  
3. **Generate & verify** — emit Kotlin and prove parity (contracts, tests, CI — Phase 4).

This repository delivers the **reference corpus**, **catalog**, **Python analyzer**, and **Kotlin codegen** for the MVP profiles; **Phase 4** adds normalized OpenAPI diff + golden HTTP parity in CI.

## Verification story (status)

Automated OpenAPI diff and golden HTTP parity checks are **Phase 4** (see roadmap). Phase 1 proves **build + unit tests** per demo (`pytest`, `./gradlew test`). **Phase 3** adds `generate` + CI smoke that runs **`./gradlew test`** on emitted Kotlin (see [pykotmig-codegen.yml](../.github/workflows/pykotmig-codegen.yml) in the monorepo root).

## Troubleshooting

- **First Gradle run is slow:** `./gradlew` downloads the Gradle distribution and Maven dependencies.  
- **Port in use:** choose another `--port` for Python, or set `PORT` before `./gradlew run` (defaults: Status Hub **8080**, Order API **8081**).  
- **uv:** run `uv sync` from each demo’s `python/` directory (each demo has its own `.venv`).

## Repository layout

| Path | Purpose |
|------|---------|
| [catalog/](catalog/README.md) | Human + machine (`manifest.json`) component index |
| [examples/status-hub/](examples/status-hub/README.md) | Minimal parity demo |
| [examples/order-api/](examples/order-api/README.md) | CRUD + client + DI demo |
| [tool/](tool/README.md) | `pykotmig-cli`: `analyze` → `analysis.json`; `generate` → Ktor+Gradle (Phase 3) |
| [.planning/](.planning/ROADMAP.md) | Roadmap, requirements, phase plans |

## Planning

Roadmap and traceable requirements live under [`.planning/`](.planning/ROADMAP.md). **Phases 1–3** (corpus, analyzer, Kotlin codegen + VER-01 smoke) are implemented in this tree; **Phase 4** adds parity diff + golden HTTP + README/CI alignment.

---

*Hand-authored reference corpus — automation lands in later phases per roadmap.*
