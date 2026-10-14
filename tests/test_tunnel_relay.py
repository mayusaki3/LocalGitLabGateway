"""Request/response correlation for the tunnel."""

import asyncio

import pytest

from local_gitlab_gateway.common.tunnel_relay import (
    TunnelDisconnected,
    TunnelRelay,
    TunnelTimeout,
)


class FakeSocket:
    def __init__(self) -> None:
        self.messages: list[dict] = []

    async def send_json(self, message: dict) -> None:
        self.messages.append(message)


@pytest.mark.asyncio
async def test_correlate_response() -> None:
    relay = TunnelRelay()
    socket = FakeSocket()
    relay.attach(socket)
    task = asyncio.create_task(
        relay.request("req_one", "GET", "/internal/api/v1/projects")
    )
    await asyncio.sleep(0)
    relay.resolve({
        "type": "response",
        "request_id": "req_one",
        "status_code": 200,
        "body": {"request_id": "req_one", "projects": []},
    })
    assert (await task).status_code == 200
    assert socket.messages[0]["request_id"] == "req_one"


@pytest.mark.asyncio
async def test_no_connection() -> None:
    with pytest.raises(TunnelDisconnected):
        await TunnelRelay().request("req_one", "GET", "/internal/api/v1/projects")


@pytest.mark.asyncio
async def test_timeout_drops_pending_request() -> None:
    relay = TunnelRelay(timeout=0.001)
    relay.attach(FakeSocket())
    with pytest.raises(TunnelTimeout):
        await relay.request("req_one", "GET", "/internal/api/v1/projects")
    assert not relay.pending


@pytest.mark.asyncio
async def test_disconnect_fails_pending_request() -> None:
    relay = TunnelRelay()
    socket = FakeSocket()
    relay.attach(socket)
    task = asyncio.create_task(
        relay.request("req_one", "GET", "/internal/api/v1/projects")
    )
    await asyncio.sleep(0)
    relay.detach(socket)
    with pytest.raises(TunnelDisconnected):
        await task


def test_unknown_response_is_ignored() -> None:
    assert not TunnelRelay().resolve({
        "type": "response",
        "request_id": "req_unknown",
        "status_code": 200,
        "body": {"request_id": "req_unknown"},
    })
