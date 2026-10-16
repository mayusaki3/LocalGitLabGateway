"""Public API -> WebSocket relay -> private HTTP -> mock GitLab roundtrip.

This exercises the actual FastAPI WebSocket ingress and request correlation
without requiring certificates, listening sockets, or a real GitLab server.
"""

import asyncio
import threading

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from local_gitlab_gateway.private_bridge.tunnel_client import forward_request
from local_gitlab_gateway.public_gateway.tunnel_api import router as api_router
from local_gitlab_gateway.public_gateway.tunnel_endpoint import (
    router as websocket_router,
)
from local_gitlab_gateway.public_gateway.tunnel_endpoint import session


@pytest.fixture
def gateway() -> TestClient:
    app = FastAPI()
    app.state.tunnel_token = "integration-tunnel-token"
    app.include_router(websocket_router)
    app.include_router(api_router)
    with TestClient(app) as client:
        yield client
    assert not session.connected


def test_project_list_roundtrip_through_real_websocket_ingress(gateway: TestClient) -> None:
    """HTTP request waits for a WebSocket response from the mock private side."""
    observed = {}

    def private_handler(request: httpx.Request) -> httpx.Response:
        observed["path"] = request.url.path
        observed["query"] = dict(request.url.params)
        observed["authorization"] = request.headers["authorization"]
        observed["request_id"] = request.headers["x-request-id"]
        return httpx.Response(
            200,
            json={
                "request_id": request.headers["x-request-id"],
                "projects": [{"id": 42, "name": "mock-project"}],
            },
        )

    response_box = {}
    failures = []

    def call_public_api() -> None:
        try:
            response_box["response"] = gateway.get(
                "/api/v1/projects?page=2&per_page=5"
            )
        except BaseException as exc:
            failures.append(exc)

    with gateway.websocket_connect(
        "/internal/tunnel/v1",
        headers={"Authorization": "Bearer integration-tunnel-token"},
        subprotocols=["lgg-tunnel.v1"],
    ) as websocket:
        thread = threading.Thread(target=call_public_api, daemon=True)
        thread.start()
        try:
            incoming = websocket.receive_json()
            assert incoming["type"] == "request"
            assert incoming["method"] == "GET"
            assert incoming["path"] == "/internal/api/v1/projects"
            assert incoming["query"] == {"page": 2, "per_page": 5}

            async def mock_private_bridge() -> dict:
                async with httpx.AsyncClient(
                    base_url="http://private-bridge",
                    transport=httpx.MockTransport(private_handler),
                ) as client:
                    return await forward_request(incoming, client, "internal-key")

            websocket.send_json(asyncio.run(mock_private_bridge()))
            thread.join(timeout=5)
            assert not thread.is_alive(), "Public API did not receive the tunnel response"
        finally:
            thread.join(timeout=1)

    assert not failures
    response = response_box["response"]
    assert response.status_code == 200
    body = response.json()
    assert body["projects"] == [{"id": 42, "name": "mock-project"}]
    assert body["request_id"] == incoming["request_id"]
    assert observed["request_id"] == incoming["request_id"]
    assert observed["path"] == "/internal/api/v1/projects"
    assert observed["query"] == {"page": "2", "per_page": "5"}
    assert observed["authorization"] == "Bearer internal-key"
