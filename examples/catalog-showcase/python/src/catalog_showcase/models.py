"""Pydantic request/response models (catalog: JSON models)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    quantity: int = Field(ge=0, le=1_000_000)


class ItemOut(BaseModel):
    id: str
    name: str
    quantity: int


class StrictScore(BaseModel):
    """Used by validation routes to demonstrate 422 on bad input."""

    score: int = Field(ge=0, le=100, description="0–100 inclusive")
