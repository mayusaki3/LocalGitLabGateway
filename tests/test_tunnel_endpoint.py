"""WebSocket ingress behavior without a running external server."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from local_gitlab_gateway.public_gateway.tunnel_endpoint import router, session


@pytest.fixture
def client() -> TestClient:
    app = FastAPI()
    app.state.tunnel_token = "test-tunnel-only-secret"
    app.include_router(router)
    with TestClient(app) as test_client:
        yield test_client
    session.socket = None


def test_missing_credential_rejected(client: TestClient) -> None:
    with pytest.raises(WebSocketDisconnect), client.websocket_connect(
        "/internal/tunnel/v1", subprotocols=["lgg-tunnel.v1"]
    ):
        pass


def test_wrong_subprotocol_rejected(client: TestClient) -> None:
    with pytest.raises(WebSocketDisconnect), client.websocket_connect(
        "/internal/tunnel/v1",
        headers={"Authorization": "Bearer test-tunnel-only-secret"},
    ):
        pass


def test_authenticated_connection_and_invalid_message(client: TestClient) -> None:
    with client.websocket_connect(
        "/internal/tunnel/v1",
        subprotocols=["lgg-tunnel.v1"],
        headers={"Authorization": "Bearer test-tunnel-only-secret"},
    ) as socket:
        assert socket.accepted_subprotocol == "lgg-tunnel.v1"
        socket.send_json({"type": "unsupported"})
        with pytest.raises(WebSocketDisconnect):
            socket.receive_json()
    assert not session.connected


def test_second_connection_rejected_without_dropping_first(client: TestClient) -> None:
    headers = {"Authorization": "Bearer test-tunnel-only-secret"}
    with client.websocket_connect(
        "/internal/tunnel/v1", subprotocols=["lgg-tunnel.v1"], headers=headers
    ) as first:
        assert session.connected
        with pytest.raises(WebSocketDisconnect) as rejected:
            with client.websocket_connect(
                "/internal/tunnel/v1", subprotocols=["lgg-tunnel.v1"], headers=headers
            ):
                pass
        assert rejected.value.code == 1013
        assert session.connected
        assert first.accepted_subprotocol == "lgg-tunnel.v1"
    assert not session.connected


def test_normal_client_disconnect_detaches_session(client: TestClient) -> None:
    with client.websocket_connect(
        "/internal/tunnel/v1",
        subprotocols=["lgg-tunnel.v1"],
        headers={"Authorization": "Bearer test-tunnel-only-secret"},
    ) as socket:
        assert session.connected
        socket.send_json({
            "type": "response",
            "request_id": "req_unknown",
            "status_code": 200,
            "body": {"request_id": "req_unknown"},
        })
    assert not session.connected
