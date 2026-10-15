"""Request/response correlation for the tunnel."""

import asyncio

import pytest

from local_gitlab_gateway.common.tunnel_relay import (
    TunnelDisconnectedError,
    TunnelRelay,
    TunnelTimeoutError,
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
    with pytest.raises(TunnelDisconnectedError):
        await TunnelRelay().request("req_one", "GET", "/internal/api/v1/projects")


@pytest.mark.asyncio
async def test_timeout_drops_pending_request() -> None:
    relay = TunnelRelay(timeout=0.001)
    relay.attach(FakeSocket())
    with pytest.raises(TunnelTimeoutError):
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
    with pytest.raises(TunnelDisconnectedError):
        await task


def test_unknown_response_is_ignored() -> None:
    assert not TunnelRelay().resolve({
        "type": "response",
        "request_id": "req_unknown",
        "status_code": 200,
        "body": {"request_id": "req_unknown"},
    })



def test_reject_second_connection_and_ignore_stale_detach() -> None:
    relay = TunnelRelay()
    first = FakeSocket()
    second = FakeSocket()
    assert relay.attach(first)
    assert relay.connected
    assert not relay.attach(second)
    relay.detach(second)
    assert relay.socket is first
    relay.detach(first)
    assert not relay.connected


@pytest.mark.asyncio
async def test_reject_duplicate_pending_request_id() -> None:
    relay = TunnelRelay()
    relay.attach(FakeSocket())
    task = asyncio.create_task(
        relay.request("req_duplicate", "GET", "/internal/api/v1/projects")
    )
    await asyncio.sleep(0)
    with pytest.raises(ValueError, match="Duplicate pending request_id"):
        await relay.request("req_duplicate", "GET", "/internal/api/v1/projects")
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert not relay.pending


@pytest.mark.asyncio
async def test_disconnect_before_send() -> None:
    relay = TunnelRelay()
    socket = FakeSocket()
    relay.attach(socket)
    await relay.send_lock.acquire()
    task = asyncio.create_task(
        relay.request("req_race", "GET", "/internal/api/v1/projects")
    )
    await asyncio.sleep(0)
    relay.detach(socket)
    relay.send_lock.release()
    with pytest.raises(TunnelDisconnectedError):
        await task
    assert not relay.pending


@pytest.mark.asyncio
async def test_duplicate_response_is_ignored() -> None:
    relay = TunnelRelay()
    relay.attach(FakeSocket())
    task = asyncio.create_task(
        relay.request("req_twice", "GET", "/internal/api/v1/projects")
    )
    await asyncio.sleep(0)
    payload = {
        "type": "response",
        "request_id": "req_twice",
        "status_code": 200,
        "body": {"request_id": "req_twice", "projects": []},
    }
    assert relay.resolve(payload)
    assert not relay.resolve(payload)
    assert (await task).status_code == 200
