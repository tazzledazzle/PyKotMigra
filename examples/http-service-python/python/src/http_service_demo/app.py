"""Minimal FastAPI service: routing + JSON + health."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field


class GreetIn(BaseModel):
    name: str = Field(min_length=1, max_length=80)


class GreetOut(BaseModel):
    message: str


def create_app() -> FastAPI:
    app = FastAPI(title="http-service-demo", version="0.1.0")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/greet", response_model=GreetOut)
    def greet(body: GreetIn) -> GreetOut:
        return GreetOut(message=f"Hello, {body.name.strip()}")

    return app


app = create_app()
