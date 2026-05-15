"""HTTP middleware: correlation id + request logging (catalog: middleware)."""

from __future__ import annotations

import logging
import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request
from starlette.responses import Response

logger = logging.getLogger("catalog_showcase.middleware")


def install_correlation_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def add_correlation_id(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        cid = request.headers.get("x-correlation-id") or str(uuid.uuid4())
        request.state.correlation_id = cid
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "request_complete",
            extra={
                "correlation_id": cid,
                "method": request.method,
                "path": request.url.path,
                "duration_ms": round(duration_ms, 3),
            },
        )
        response.headers["x-correlation-id"] = cid
        return response
