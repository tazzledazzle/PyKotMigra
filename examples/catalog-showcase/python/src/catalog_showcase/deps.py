"""In-memory store + FastAPI Depends (catalog: dependency injection)."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from catalog_showcase.config import Settings, get_settings


class ItemStore:
    """Tiny in-memory store for demo DI."""

    def __init__(self) -> None:
        self._seq = 0
        self._items: dict[str, tuple[str, int]] = {}

    def create(self, name: str, quantity: int) -> str:
        self._seq += 1
        iid = f"it-{self._seq}"
        self._items[iid] = (name, quantity)
        return iid

    def get(self, item_id: str) -> tuple[str, int] | None:
        return self._items.get(item_id)

    def list_ids(self) -> list[str]:
        return list(self._items.keys())


_store = ItemStore()


def get_store() -> ItemStore:
    return _store


def get_settings_dep() -> Settings:
    return get_settings()


SettingsDep = Annotated[Settings, Depends(get_settings_dep)]
StoreDep = Annotated[ItemStore, Depends(get_store)]
