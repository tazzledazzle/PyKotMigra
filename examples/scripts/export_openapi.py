#!/usr/bin/env python3
"""Regenerate committed OpenAPI JSON for reference demos (Phase 4 contract baseline).

Run from the demo’s ``python/`` directory (after ``uv sync``):

```bash
# Status Hub
cd examples/status-hub/python && uv run python ../../scripts/export_openapi.py status-hub

# Order API
cd examples/order-api/python && uv run python ../../scripts/export_openapi.py order-api

# HTTP service
cd examples/http-service-python/python && uv run python ../../scripts/export_openapi.py http-service-python

# Catalog showcase
cd examples/catalog-showcase/python && uv run python ../../scripts/export_openapi.py catalog-showcase
```
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _write(path: Path, schema: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(schema, indent=2, sort_keys=True) + "\n"
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "demo",
        choices=("status-hub", "order-api", "http-service-python", "catalog-showcase"),
        help="Which FastAPI demo to export",
    )
    args = parser.parse_args()

    demos: dict[str, tuple[str, str, str]] = {
        "status-hub": ("status_hub.app", "app", "status-hub"),
        "order-api": ("order_api.app", "app", "order-api"),
        "http-service-python": ("http_service_demo.app", "app", "http-service-python"),
        "catalog-showcase": ("catalog_showcase.app", "app", "catalog-showcase"),
    }
    import importlib

    mod_path, attr_name, folder = demos[args.demo]
    mod = importlib.import_module(mod_path)
    app = getattr(mod, attr_name)
    root = Path(__file__).resolve().parents[1] / folder / "contracts"
    _write(root / "openapi.json", app.openapi())
    print(f"Wrote {root / 'openapi.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
