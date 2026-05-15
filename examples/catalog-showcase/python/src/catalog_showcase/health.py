"""Health and readiness (catalog: health / readiness)."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def liveness() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
def readiness() -> dict[str, str]:
    """Stub readiness — extend with DB ping etc."""
    return {"ready": "true"}
