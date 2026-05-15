#!/usr/bin/env python3
"""Regenerate committed OpenAPI JSON for reference demos (Phase 4 contract baseline).

Run from the demo’s ``python/`` directory (after ``uv sync``):

```bash
# Status Hub
cd examples/status-hub/python && uv run python ../../scripts/export_openapi.py status-hub

# Order API
cd examples/order-api/python && uv run python ../../scripts/export_openapi.py order-api
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
        choices=("status-hub", "order-api"),
        help="Which reference demo to export",
    )
    args = parser.parse_args()

    if args.demo == "status-hub":
        from status_hub.app import app

        root = Path(__file__).resolve().parents[1] / "status-hub" / "contracts"
        _write(root / "openapi.json", app.openapi())
        print(f"Wrote {root / 'openapi.json'}")
        return 0

    if args.demo == "order-api":
        from order_api.app import app

        root = Path(__file__).resolve().parents[1] / "order-api" / "contracts"
        _write(root / "openapi.json", app.openapi())
        print(f"Wrote {root / 'openapi.json'}")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
