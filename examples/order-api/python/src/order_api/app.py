from __future__ import annotations

from dataclasses import dataclass, field
from typing import Annotated
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from order_api.config import Settings
from order_api.logging_conf import configure_logging
from order_api.notify_client import notify_order_created


@dataclass
class OrderStore:
    orders: dict[str, "Order"] = field(default_factory=dict)


class Order(BaseModel):
    id: str
    title: str = Field(min_length=1, max_length=200)


class CreateOrderBody(BaseModel):
    title: str = Field(min_length=1, max_length=200)


_store = OrderStore()


def get_settings() -> Settings:
    return Settings()


def get_store() -> OrderStore:
    return _store


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="order-api", version="0.1.0")

    @app.post("/orders", response_model=Order, status_code=status.HTTP_201_CREATED)
    def create_order(
        body: CreateOrderBody,
        store: Annotated[OrderStore, Depends(get_store)],
        settings: Annotated[Settings, Depends(get_settings)],
    ) -> Order:
        oid = str(uuid4())
        order = Order(id=oid, title=body.title.strip())
        store.orders[oid] = order
        notify_order_created(settings.external_http_url, oid)
        return order

    @app.get("/orders/{order_id}", response_model=Order)
    def get_order(
        order_id: str,
        store: Annotated[OrderStore, Depends(get_store)],
    ) -> Order:
        o = store.orders.get(order_id)
        if not o:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="order not found")
        return o

    @app.get("/orders", response_model=list[Order])
    def list_orders(store: Annotated[OrderStore, Depends(get_store)]) -> list[Order]:
        return list(store.orders.values())

    @app.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_order(
        order_id: str,
        store: Annotated[OrderStore, Depends(get_store)],
    ) -> None:
        if order_id not in store.orders:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="order not found")
        del store.orders[order_id]

    return app


app = create_app()
