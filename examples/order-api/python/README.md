# Order API — Python

```bash
uv sync --extra dev
uv run pytest
uv run uvicorn order_api.app:app --host 127.0.0.1 --port 8081
```

Set `EXTERNAL_HTTP_URL` to enable outbound notify on create (optional).
