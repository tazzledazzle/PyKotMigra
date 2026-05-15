# Example contracts (Phase 4 baseline)

Each reference demo keeps a **canonical OpenAPI 3** snapshot next to its code:

| Demo | Contract file | Regenerate |
|------|---------------|------------|
| Status Hub | [../status-hub/contracts/openapi.json](../status-hub/contracts/openapi.json) | `cd examples/status-hub/python && uv run python ../../scripts/export_openapi.py status-hub` |
| Order API | [../order-api/contracts/openapi.json](../order-api/contracts/openapi.json) | `cd examples/order-api/python && uv run python ../../scripts/export_openapi.py order-api` |

**Parity bar (demos):**

1. **OpenAPI snapshot** — committed JSON must match `app.openapi()` from the FastAPI app (normalized with `sort_keys=True`). Enforced by `tests/test_openapi_contract.py` in each Python demo.
2. **Golden HTTP (success paths)** — Kotlin `ApplicationTest` asserts the same JSON bodies and status codes as the Python tests for `/health`, `/version`, `/echo` (valid), and Order API CRUD + 404.
3. **Validation** — invalid echo input returns **422** on both stacks (body shape may differ; FastAPI uses Pydantic’s `detail` list; Kotlin returns a minimal `detail` string for demos).
4. **Outbound notify** — Kotlin `HttpClient` uses the same **2s request timeout** semantics as Python `httpx.Client(timeout=2.0)`.
