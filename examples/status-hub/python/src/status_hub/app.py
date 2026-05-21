# app.py
from __future__ import annotations

import logging
import os
import time
import uuid
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, Field, field_validator
from starlette.responses import Response

from status_hub.background_tasks import (
    completed_job_ids,
    demo_async_work,
    reset_completed_for_tests,
)

# Re-export for tests that import hooks from `status_hub.app`.
reset_completed_jobs_for_tests = reset_completed_for_tests

logger = logging.getLogger("status_hub")


def _expected_api_key() -> str:
    # Read per-request to support runtime key rotation (12-factor style).
    # If this becomes a hot path, cache with a short TTL instead.
    return os.environ.get("STATUS_HUB_API_KEY", "demo-key")


# ── models ────────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str = "ok"


class VersionResponse(BaseModel):
    name: str = "status-hub"
    version: str = "0.1.0"


class EchoRequest(BaseModel):
    message: str
    count: int = Field(ge=1, le=100)

    @field_validator("message", mode="before")
    @classmethod
    def strip_and_validate_message(cls, v: str) -> str:
        # Strip BEFORE min_length check so "   " is correctly rejected
        stripped = v.strip()
        if not stripped:
            raise ValueError("message must not be blank or whitespace-only")
        return stripped


class EchoResponse(BaseModel):
    message: str
    count: int


# ── factory ───────────────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    app = FastAPI(title="status-hub", version="0.1.0")

    @app.middleware("http")
    async def add_correlation_id(
            request: Request,
            call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        cid = request.headers.get("x-correlation-id") or str(uuid.uuid4())
        request.state.correlation_id = cid
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "request",
            extra={
                "correlation_id": cid,
                "method": request.method,
                "path": request.url.path,
                "duration_ms": round(duration_ms, 2),
            },
        )
        response.headers["x-correlation-id"] = cid
        return response

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse()

    @app.get("/version", response_model=VersionResponse)
    def version() -> VersionResponse:
        return VersionResponse()

    @app.post("/echo", response_model=EchoResponse)
    def echo(body: EchoRequest) -> EchoResponse:
        return EchoResponse(message=body.message, count=body.count)

    @app.post("/jobs", status_code=202)
    def schedule_job(background_tasks: BackgroundTasks) -> dict[str, Any]:
        job_id = str(uuid.uuid4())
        background_tasks.add_task(demo_async_work, job_id)
        return {"job_id": job_id, "status": "accepted"}

    @app.get("/secure/ping")
    def secure_ping(
            x_api_key: str | None = Header(default=None, alias="x-api-key"),
    ) -> dict[str, str]:
        if not x_api_key or x_api_key != _expected_api_key():
            raise HTTPException(status_code=401, detail="invalid or missing API key")
        return {"authenticated": "yes"}

    return app


# Entrypoint for uvicorn: `uvicorn status_hub.app:app`
# Intentionally after create_app() definition — not executed on import by tests.
app = create_app()