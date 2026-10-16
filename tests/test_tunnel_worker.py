"""FW-side tunnel worker tests with an in-memory WebSocket fake."""

import asyncio
import json

import httpx
import pytest

from local_gitlab_gateway.private_bridge import tunnel_worker
from local_gitlab_gateway.private_bridge.tunnel_worker import (
    process_message,
    reconnect_delay,
)


class FakeSocket:
    def __init__(self) -> None:
        self.sent = []
        self.closed = []

    async def send(self, value: str) -> None:
        self.sent.append(json.loads(value))

    async def close(self, code: int) -> None:
        self.closed.append(code)


@pytest.mark.asyncio
async def test_process_project_list_request() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["x-request-id"] == "req_one"
        return httpx.Response(200, json={"request_id": "req_one", "projects": []})

    socket = FakeSocket()
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="http://bridge"
    ) as client:
        await process_message(
            socket,
            json.dumps({"type": "request", "request_id": "req_one",
                        "method": "GET", "path": "/internal/api/v1/projects",
                        "query": {}, "body": None}),
            client,
            "internal-key",
        )
    assert socket.sent[0]["body"]["projects"] == []


@pytest.mark.asyncio
async def test_reject_disallowed_route_without_forwarding() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError("Unapproved route was forwarded")

    socket = FakeSocket()
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="http://bridge"
    ) as client:
        await process_message(
            socket,
            json.dumps({"type": "request", "request_id": "req_one",
                        "method": "GET",
                        "path": "/internal/api/v1/projects/1/secret"}),
            client,
            "internal-key",
        )
    assert socket.sent[0]["status_code"] == 403
    assert socket.sent[0]["body"]["request_id"] == "req_one"


def test_reconnect_backoff() -> None:
    assert [reconnect_delay(n) for n in (0, 1, 2, 6)] == [1, 2, 4, 30]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "raw",
    [
        "{",
        "null",
        json.dumps({"type": "request", "request_id": "invalid", "method": "GET",
                    "path": "/internal/api/v1/projects"}),
    ],
)
async def test_invalid_frame_closes_socket(raw: str) -> None:
    socket = FakeSocket()
    async with httpx.AsyncClient(base_url="http://bridge") as client:
        await process_message(socket, raw, client, "internal-key")
    assert socket.closed == [1008]
    assert socket.sent == []


@pytest.mark.asyncio
async def test_private_bridge_http_failure_returns_502() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("unreachable", request=request)

    socket = FakeSocket()
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="http://bridge"
    ) as client:
        await process_message(
            socket,
            json.dumps({"type": "request", "request_id": "req_failed",
                        "method": "GET", "path": "/internal/api/v1/projects"}),
            client,
            "internal-key",
        )
    assert socket.sent[0]["status_code"] == 502
    assert socket.sent[0]["body"]["request_id"] == "req_failed"
    assert socket.sent[0]["body"]["error"]["code"] == "private_bridge_unavailable"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "wss_url,token,bridge,key,error",
    [
        ("ws://example.invalid/tunnel", "token", "http://bridge", "key", "wss://"),
        ("wss://example.invalid/tunnel", "", "http://bridge", "key", "Missing"),
    ],
)
async def test_worker_rejects_invalid_configuration(
    wss_url: str, token: str, bridge: str, key: str, error: str
) -> None:
    with pytest.raises(ValueError, match=error):
        await tunnel_worker.run_worker(wss_url, token, bridge, key)


@pytest.mark.asyncio
async def test_worker_connects_and_retries(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = []

    class FakeConnection:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        def __aiter__(self):
            async def frames():
                yield json.dumps({"type": "request", "request_id": "req_worker",
                                  "method": "GET", "path": "/internal/api/v1/projects"})
            return frames()

        async def send(self, value: str) -> None:
            calls.append(json.loads(value))

    def fake_connect(*args, **kwargs):
        assert kwargs["subprotocols"] == ["lgg-tunnel.v1"]
        assert kwargs["additional_headers"]["Authorization"] == "Bearer token"
        return FakeConnection()

    async def fake_forward(payload, client, key):
        assert key == "internal-key"
        return {"type": "response", "request_id": "req_worker",
                "status_code": 200, "body": {"request_id": "req_worker"}}

    async def stop_after_first_sleep(delay):
        assert delay == 1
        raise asyncio.CancelledError

    monkeypatch.setattr(tunnel_worker, "connect", fake_connect)
    monkeypatch.setattr(tunnel_worker, "forward_request", fake_forward)
    monkeypatch.setattr(tunnel_worker.asyncio, "sleep", stop_after_first_sleep)
    with pytest.raises(asyncio.CancelledError):
        await tunnel_worker.run_worker(
            "wss://example.invalid/tunnel", "token", "http://bridge", "internal-key"
        )
    assert calls[0]["status_code"] == 200


@pytest.mark.asyncio
async def test_worker_retries_connection_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    def failing_connect(*args, **kwargs):
        raise OSError("connection refused")

    async def stop_after_retry(delay):
        assert delay == 1
        raise asyncio.CancelledError

    monkeypatch.setattr(tunnel_worker, "connect", failing_connect)
    monkeypatch.setattr(tunnel_worker.asyncio, "sleep", stop_after_retry)
    with pytest.raises(asyncio.CancelledError):
        await tunnel_worker.run_worker(
            "wss://example.invalid/tunnel", "token", "http://bridge", "internal-key"
        )
