import time
import httpx
import pytest
import respx
from fastapi.testclient import TestClient

from catalog_showcase.app import create_app
from catalog_showcase.background_tasks import completed_job_ids, reset_completed_for_tests


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def _reset_job_state() -> None:
    """Ensure job-completion state is clean before every test."""
    reset_completed_for_tests()


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())


# ── helpers ───────────────────────────────────────────────────────────────────

def _wait_for(condition, *, timeout: float = 1.0, interval: float = 0.01) -> bool:
    """Poll `condition()` until True or timeout. Returns final condition value."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if condition():
            return True
        time.sleep(interval)
    return condition()


# ── tests ─────────────────────────────────────────────────────────────────────

def test_health(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_create_item(client: TestClient) -> None:
    r = client.post("/items", json={"name": "a", "quantity": 2})
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "a"
    assert "id" in data, f"Response missing 'id': {data}"


def test_get_item(client: TestClient) -> None:
    create = client.post("/items", json={"name": "a", "quantity": 2})
    assert create.status_code == 200, f"Setup POST failed: {create.text}"
    iid = create.json()["id"]

    r = client.get(f"/items/{iid}")
    assert r.status_code == 200
    assert r.json()["quantity"] == 2


def test_validation_rejects_out_of_range_score(client: TestClient) -> None:
    r = client.post("/validation-demo/score", json={"score": 101})
    assert r.status_code == 422


def test_auth_rejects_missing_key(client: TestClient) -> None:
    r = client.get("/secure/ping")
    assert r.status_code == 401


def test_auth_accepts_valid_key(client: TestClient) -> None:
    r = client.get("/secure/ping", headers={"x-api-key": "demo-key"})
    assert r.status_code == 200


@respx.mock
def test_upstream_sample_uses_client(client: TestClient) -> None:
    # NOTE: requires the app to use httpx.AsyncClient/Client injected or
    # module-level so respx can intercept it.
    respx.get("https://jsonplaceholder.typicode.com/posts/1").mock(
        return_value=httpx.Response(200, json={"id": 1, "title": "x"})
    )
    r = client.get("/upstream-sample")
    assert r.status_code == 200
    assert r.json()["id"] == 1


def test_background_task_completes(client: TestClient) -> None:
    r = client.post("/jobs")
    assert r.status_code == 202

    completed = _wait_for(completed_job_ids, timeout=1.0)
    assert completed, "Background task did not complete within 1 second"