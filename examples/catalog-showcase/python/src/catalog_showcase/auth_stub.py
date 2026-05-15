"""API-key style auth stub (catalog: auth stub — v2 narrative)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import APIKeyHeader

from catalog_showcase.config import get_settings

router = APIRouter(prefix="/secure", tags=["auth"])

_api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)


async def require_api_key(api_key: str | None = Security(_api_key_header)) -> str:
    expected = get_settings().api_key
    if not api_key or api_key != expected:
        raise HTTPException(status_code=401, detail="invalid or missing API key")
    return api_key


@router.get("/ping")
def protected_ping(_: str = Depends(require_api_key)) -> dict[str, str]:
    return {"authenticated": "yes"}
