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


@respx.mock
def test_notify_on_create(monkeypatch: pytest.MonkeyPatch) -> None:
    route = respx.post("https://example.test/notify").mock(return_value=Response(204))
    monkeypatch.setenv("EXTERNAL_HTTP_URL", "https://example.test")
    r = client.post("/orders", json={"title": "x"})
    assert r.status_code == 201
    assert route.called
