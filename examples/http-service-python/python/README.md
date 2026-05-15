# http-service-demo

FastAPI microservice: `/health`, `/greet`.

```bash
uv sync --extra dev
uv run pytest -q
uv run mypy src/http_service_demo
uv run ruff check src tests
uv run uvicorn http_service_demo.app:app --reload --port 8010
```
