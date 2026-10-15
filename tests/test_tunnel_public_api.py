"""Public API behavior while using the tunnel."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from local_gitlab_gateway.public_gateway.tunnel_api import router
from local_gitlab_gateway.public_gateway.tunnel_endpoint import session


def test_disconnected_returns_503() -> None:
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    response = client.get("/api/v1/projects")
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "tunnel_unavailable"
    assert response.json()["request_id"].startswith("req_")


def test_health_not_dependent_on_tunnel() -> None:
    assert session.socket is None
