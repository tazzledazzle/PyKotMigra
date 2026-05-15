# PyKotMig CLI (`tool/`)

Installable **uv** project: **`analyze`** scans a FastAPI-style Python layout (`pyproject.toml` + `src/`) and writes **`analysis.json`**; **`generate`** reads that file and writes a **Ktor + Gradle** project (profiles **`status-hub`** and **`order-api`**).

## Security

`--app module:attr` uses **importlib** in your local process. Only run against **trusted** repositories. There is no sandbox.

## Commands

Console script: **`pykotmig-cli`**. Subcommands:

- `pykotmig-cli analyze …`
- `pykotmig-cli generate …`
- `pykotmig-cli verify …` — run `gradlew` on a generated tree; **`--llm`** sends failing logs plus key Gradle/Kotlin snippets to an OpenAI-compatible **`/v1/chat/completions`** endpoint and applies returned file patches (set **`OPENAI_API_KEY`** or **`PYKOTMIG_OPENAI_API_KEY`**; optional **`OPENAI_BASE_URL`**). With **`--llm --dry-run`**, the model still runs, then **stderr** gets Gradle tail, context file bodies, the user JSON payload, and **full** proposed file contents (nothing is written under `--project`).

Or: `uv run python -m pykotmig --help` / `python -m pykotmig analyze --help`.

## Analyze (from `tool/`)

```bash
uv sync --extra dev
uv run pykotmig-cli analyze \
  --project-root ../examples/order-api/python \
  --app order_api.app:app \
  --out ../examples/order-api/python/analysis.json
```

| Flag | Meaning |
|------|---------|
| `--project-root` | Directory containing `pyproject.toml` and `src/` |
| `--app` | `module:attr` for the FastAPI instance |
| `--out` | Output path for `analysis.json` |
| `--force` | Bypass `.pykotmig/cache/` incremental parse cache |
| `--mypy` | Run `mypy src` (requires `mypy` on `PATH`) |
| `--dry-run` | Do not write `--out` or update `.pykotmig/cache/`; print analysis JSON to **stdout**. With default **Ollama** OpenAPI, prints request debug to **stderr** and **skips** the HTTP call (`openapi` in JSON will be `null`). |
| **OpenAPI source** | Default: **Ollama** — `analyze` sends `src/**/*.py` to `OLLAMA_HOST` (default `http://127.0.0.1:11434`) `POST /api/chat` with `format: json` to infer OpenAPI; set **`PYKOTMIG_OLLAMA_MODEL`** / `OLLAMA_MODEL` (default `llama3.2`). For the previous behavior (import app and call `app.openapi()`), set **`PYKOTMIG_OPENAPI_SOURCE=fastapi`**. |

## Generate

Requires a successful **`openapi`** section in `analysis.json` (run `analyze` on the matching demo).

```bash
uv run pykotmig-cli generate \
  --analysis ../examples/order-api/python/analysis.json \
  --out /tmp/pykotmig-gen-order \
  --kotlin-package dev.pykotmig.gen.orderapi \
  --project-name gen-order-api \
  --profile order-api \
  --force
```

| Flag | Meaning |
|------|---------|
| `--analysis` | Path to `analysis.json` |
| `--out` | Output directory (created; use `--force` to replace) |
| `--kotlin-package` | Kotlin package for generated sources |
| `--project-name` | `settings.gradle.kts` `rootProject.name` |
| `--profile` | `status-hub` or `order-api` (must match analyzed service) |
| `--allow-errors` | Allow codegen when `errors[]` is non-empty (unsafe) |

Generated tree includes a vendored **Gradle wrapper**; run `bash ./gradlew test` from `--out`.

## JSON schema

`tool/schemas/analysis-v1.schema.json` describes `analysis.json` (Pydantic-derived).

## Tests

```bash
uv sync --extra dev
uv run pytest
```

Integration tests run **`bash ./gradlew test`** on generated output when **JDK 17+** is on `PATH`.
