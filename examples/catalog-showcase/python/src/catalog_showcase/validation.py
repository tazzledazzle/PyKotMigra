"""Strict validation → automatic 422 (catalog: validation / 422)."""

from __future__ import annotations

from fastapi import APIRouter

from catalog_showcase.models import StrictScore

router = APIRouter(prefix="/validation-demo", tags=["validation"])


@router.post("/score", response_model=StrictScore)
def echo_score(body: StrictScore) -> StrictScore:
    """POST e.g. {\"score\": 101} or {\"score\": -1} → 422 from Pydantic."""
    return body
