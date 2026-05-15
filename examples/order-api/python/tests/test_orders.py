import pytest
import respx
from fastapi.testclient import TestClient
from httpx import Response

from order_api.app import app

client = TestClient(app)


def test_create_and_get_order() -> None:
    r = client.post("/orders", json={"title": "  Book  "})
    assert r.status_code == 201
    data = r.json()
    assert "id" in data
    assert data["title"] == "Book"
    oid = data["id"]
    r2 = client.get(f"/orders/{oid}")
    assert r2.status_code == 200
    assert r2.json()["title"] == "Book"


def test_get_missing() -> None:
    r = client.get("/orders/does-not-exist")
    assert r.status_code == 404
    assert r.text == '{"detail":"order not found"}'
    assert r.json() == {"detail": "order not found"}


def test_list_orders() -> None:
    r = client.post("/orders", json={"title": "a"})
    assert r.status_code == 201
    oid = r.json()["id"]
    r2 = client.get("/orders")
    assert r2.status_code == 200
    data = r2.json()
    assert len(data) == 1
    assert data[0] == {"id": oid, "title": "a"}


def test_delete_order() -> None:
    r = client.post("/orders", json={"title": "b"})
    assert r.status_code == 201
    oid = r.json()["id"]
    r2 = client.delete(f"/orders/{oid}")
    assert r2.status_code == 204
    r3 = client.get(f"/orders/{oid}")
    assert r3.status_code == 404


def test_title_too_long_returns_422() -> None:
    r = client.post("/orders", json={"title": "x" * 201})
    assert r.status_code == 422


@respx.mock
def test_notify_on_create(monkeypatch: pytest.MonkeyPatch) -> None:
    route = respx.post("https://example.test/notify").mock(return_value=Response(204))
    monkeypatch.setenv("EXTERNAL_HTTP_URL", "https://example.test")
    r = client.post("/orders", json={"title": "x"})
    assert r.status_code == 201
    assert route.called
