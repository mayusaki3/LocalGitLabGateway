"""Request ID propagation at the private bridge boundary."""

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from local_gitlab_gateway.common.middleware.request_id import request_id_middleware


@pytest.fixture
def client() -> TestClient:
    app = FastAPI()
    app.middleware("http")(request_id_middleware)

    @app.get("/internal/api/v1/projects")
    def internal(request: Request) -> dict:
        return {"request_id": request.state.request_id}

    @app.get("/health")
    def public(request: Request) -> dict:
        return {"request_id": request.state.request_id}

    return TestClient(app)


def test_internal_request_preserves_gateway_id(client: TestClient) -> None:
    response = client.get(
        "/internal/api/v1/projects", headers={"X-Request-ID": "req_abc123"}
    )
    assert response.json()["request_id"] == "req_abc123"
    assert response.headers["X-Request-ID"] == "req_abc123"


def test_public_request_does_not_trust_client_id(client: TestClient) -> None:
    response = client.get("/health", headers={"X-Request-ID": "req_attacker"})
    assert response.json()["request_id"] != "req_attacker"
