import pytest

from order_api.app import _store


@pytest.fixture(autouse=True)
def clear_orders() -> None:
    _store.orders.clear()
    yield
    _store.orders.clear()
