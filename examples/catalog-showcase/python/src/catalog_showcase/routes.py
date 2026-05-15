"""HTTP routes beyond health (catalog: HTTP routes)."""

from __future__ import annotations

from fastapi import APIRouter

from catalog_showcase.deps import StoreDep
from catalog_showcase.models import ItemCreate, ItemOut

router = APIRouter(prefix="/items", tags=["items"])


@router.get("", response_model=list[str])
def list_item_ids(store: StoreDep) -> list[str]:
    return store.list_ids()


@router.post("", response_model=ItemOut)
def create_item(body: ItemCreate, store: StoreDep) -> ItemOut:
    iid = store.create(body.name, body.quantity)
    return ItemOut(id=iid, name=body.name, quantity=body.quantity)


@router.get("/{item_id}", response_model=ItemOut)
def get_item(item_id: str, store: StoreDep) -> ItemOut:
    row = store.get(item_id)
    if row is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="not found")
    name, qty = row
    return ItemOut(id=item_id, name=name, quantity=qty)
