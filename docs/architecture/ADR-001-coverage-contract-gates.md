# ADR-001: Coverage and contract verification gates

## Status

Accepted

## Context

PyKotMig is a portfolio migration toolkit whose correctness story spans three layers:

1. **Unit behavior** — Python demos and the `pykotmig` CLI (`analyze`, `generate`, `verify`).
2. **Committed contracts** — OpenAPI JSON snapshots for FastAPI reference apps.
3. **Cross-stack parity** — Kotlin golden HTTP tests for Status Hub and Order API.

Examples already enforced high pytest-cov floors (92–96%), but thresholds were inconsistent, `http-service-python` and `catalog-showcase` lacked OpenAPI contract tests, and the `tool/` package had no coverage gate (≈69% measured).

## Decision

Adopt a **uniform 85% line-coverage floor** on every Python package in `examples/*/python` and `tool/`, enforced via `pytest --cov-fail-under=85`.

Extend the **contract ladder** to all FastAPI examples that ship HTTP APIs:

| Tier | Check | Demos |
|------|--------|-------|
| C1 | `app.openapi()` matches committed `contracts/openapi.json` | status-hub, order-api, http-service-python, catalog-showcase |
| C2 | Golden HTTP JSON (Kotlin `ApplicationTest`) | status-hub, order-api |
| C3 | `./gradlew test` (Kotlin unit + smoke) | All examples with `kotlin/` |

CI runs the examples matrix (Python + Kotlin) and a dedicated **tool** job with the same coverage gate.

## Alternatives considered

- **Keep per-demo thresholds (92–96%)** — Stronger locally but inconsistent; does not address tool gaps or missing contracts.
- **85% repo-wide aggregate** — Hides weak modules (e.g. `verify_loop`); rejected in favor of per-package floors.
- **Skip LLM verify paths in coverage** — Would lower signal; rejected; verify paths are tested with mocked Gradle/HTTP instead.

## Consequences

- **Positive:** One number (85%) for contributors; FastAPI contract drift fails CI; tool CLI paths gain in-process tests.
- **Negative:** Slightly more test maintenance when adding catalog components or CLI flags.
- **Operational:** Regenerate OpenAPI via `examples/scripts/export_openapi.py` when routes or models change.

## Trade-offs

Consistency and contract safety are prioritised over minimizing test volume. Kotlin Jacoco at 85% is deferred (Gradle tests already gate behavior; Python + OpenAPI cover API contracts).
