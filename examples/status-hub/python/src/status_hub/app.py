from __future__ import annotations

import logging
import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request
from starlette.responses import Response
from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger("status_hub")


class HealthResponse(BaseModel):
    status: str = "ok"


class VersionResponse(BaseModel):
    name: str = "status-hub"
    version: str = "0.1.0"


class EchoRequest(BaseModel):
    message: str = Field(min_length=1)
    count: int = Field(ge=1, le=100)

    @field_validator("message")
    @classmethod
    def strip_message(cls, v: str) -> str:
        return v.strip()


class EchoResponse(BaseModel):
    message: str
    count: int


def create_app() -> FastAPI:
    app = FastAPI(title="status-hub", version="0.1.0")

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

    return app


app = create_app()
