"""FW-side tunnel worker tests with an in-memory WebSocket fake."""

import json

import httpx
import pytest

from local_gitlab_gateway.private_bridge.tunnel_worker import (
    process_message,
    reconnect_delay,
)


class FakeSocket:
    def __init__(self) -> None:
        self.sent = []

    async def send(self, value: str) -> None:
        self.sent.append(json.loads(value))


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
