# Status Hub — Python

```bash
uv sync --extra dev
uv run pytest
uv run uvicorn status_hub.app:app --host 127.0.0.1 --port 8080
```

- `GET /health` → `{"status":"ok"}`
- `GET /version` → `{"name":"status-hub","version":"0.1.0"}`
- `POST /echo` → echoes validated JSON (`message` string, `count` int ≥ 1)
