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
    response_sent = asyncio.Event()

    class FakeConnection:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        def __aiter__(self):
            async def frames():
                yield json.dumps({"type": "request", "request_id": "req_worker",
                                  "method": "GET", "path": "/internal/api/v1/projects"})
                await asyncio.wait_for(response_sent.wait(), timeout=1)
            return frames()

        async def send(self, value: str) -> None:
            calls.append(json.loads(value))
            response_sent.set()

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


@pytest.mark.asyncio
async def test_worker_increments_retry_attempt(monkeypatch: pytest.MonkeyPatch) -> None:
    delays = []

    def failing_connect(*args, **kwargs):
        raise OSError("offline")

    async def fake_sleep(delay):
        delays.append(delay)
        if len(delays) == 2:
            raise asyncio.CancelledError

    monkeypatch.setattr(tunnel_worker, "connect", failing_connect)
    monkeypatch.setattr(tunnel_worker.asyncio, "sleep", fake_sleep)
    with pytest.raises(asyncio.CancelledError):
        await tunnel_worker.run_worker(
            "wss://example.invalid/tunnel", "token", "http://bridge", "internal-key"
        )
    assert delays == [1, 2]


def test_main_uses_environment_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    values = {
        "LGG_TUNNEL_WSS_URL": "wss://example.invalid/tunnel",
        "LGG_TUNNEL_TOKEN": "token",
        "LGG_PRIVATE_BRIDGE_URL": "http://bridge",
        "LGG_INTERNAL_API_KEY": "internal-key",
    }
    for key, value in values.items():
        monkeypatch.setenv(key, value)

    observed = {}

    async def fake_run_worker(wss_url, tunnel_token, private_bridge_url, internal_api_key):
        observed["args"] = (
            wss_url, tunnel_token, private_bridge_url, internal_api_key
        )

    monkeypatch.setattr(tunnel_worker, "run_worker", fake_run_worker)
    tunnel_worker.main()
    assert observed["args"] == (
        values["LGG_TUNNEL_WSS_URL"],
        values["LGG_TUNNEL_TOKEN"],
        values["LGG_PRIVATE_BRIDGE_URL"],
        values["LGG_INTERNAL_API_KEY"],
    )


def test_module_entrypoint_calls_main(monkeypatch: pytest.MonkeyPatch) -> None:
    import runpy

    calls = []

    def fake_asyncio_run(coroutine):
        calls.append(coroutine)
        coroutine.close()

    monkeypatch.setattr(asyncio, "run", fake_asyncio_run)
    runpy.run_path(tunnel_worker.__file__, run_name="__main__")
    assert len(calls) == 1


@pytest.mark.asyncio
async def test_worker_handles_fast_request_before_slow_request_completes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The fast response must arrive before a blocked slow response."""
    slow_started = asyncio.Event()
    release_slow = asyncio.Event()
    fast_sent = asyncio.Event()
    responses = []

    class ConcurrentSocket:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        def __aiter__(self):
            async def frames():
                yield json.dumps({"type": "request", "request_id": "req_slow",
                                  "method": "GET", "path": "/internal/api/v1/projects",
                                  "query": {"page": 99}})
                # The second frame is available immediately; no artificial stall.
                yield json.dumps({"type": "request", "request_id": "req_fast",
                                  "method": "GET", "path": "/internal/api/v1/projects",
                                  "query": {"page": 2}})
                await asyncio.wait_for(fast_sent.wait(), timeout=0.5)
                release_slow.set()
                await asyncio.sleep(0.01)
                raise asyncio.CancelledError

            return frames()

        async def send(self, value: str) -> None:
            response = json.loads(value)
            responses.append(response)
            if response["request_id"] == "req_fast":
                fast_sent.set()

    async def fake_forward(payload, client, key):
        request_id = payload["request_id"]
        if request_id == "req_slow":
            slow_started.set()
            await release_slow.wait()
        return {"type": "response", "request_id": request_id,
                "status_code": 200, "body": {"request_id": request_id}}

    monkeypatch.setattr(tunnel_worker, "connect", lambda *args, **kwargs: ConcurrentSocket())
    monkeypatch.setattr(tunnel_worker, "forward_request", fake_forward)

    try:
        with pytest.raises(asyncio.CancelledError):
            await asyncio.wait_for(
                tunnel_worker.run_worker(
                    "wss://example.invalid/tunnel", "token", "http://bridge", "internal-key"
                ),
                timeout=2,
            )
    finally:
        release_slow.set()
    assert responses[0]["request_id"] == "req_fast"


@pytest.mark.asyncio
async def test_worker_applies_in_flight_backpressure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The worker waits for capacity before scheduling another request."""
    release_first = asyncio.Event()
    first_started = asyncio.Event()
    second_started = asyncio.Event()
    responses = []

    class Socket:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        def __aiter__(self):
            async def frames():
                for request_id in ("req_first", "req_second"):
                    yield json.dumps({
                        "type": "request", "request_id": request_id,
                        "method": "GET", "path": "/internal/api/v1/projects",
                    })
                await asyncio.wait_for(second_started.wait(), timeout=1)
                raise asyncio.CancelledError
            return frames()

        async def send(self, value: str) -> None:
            responses.append(json.loads(value))

    async def forward(payload, client, key):
        if payload["request_id"] == "req_first":
            first_started.set()
            await release_first.wait()
        else:
            second_started.set()
        return {"type": "response", "request_id": payload["request_id"],
                "status_code": 200, "body": {"request_id": payload["request_id"]}}

    monkeypatch.setattr(tunnel_worker, "MAX_IN_FLIGHT", 1)
    monkeypatch.setattr(tunnel_worker, "connect", lambda *args, **kwargs: Socket())
    monkeypatch.setattr(tunnel_worker, "forward_request", forward)

    worker = asyncio.create_task(
        tunnel_worker.run_worker(
            "wss://example.invalid/tunnel", "token", "http://bridge", "internal-key"
        )
    )
    try:
        await asyncio.wait_for(first_started.wait(), timeout=1)
        # With a single slot, the second request cannot start yet.
        assert not second_started.is_set()
        release_first.set()
        await asyncio.wait_for(second_started.wait(), timeout=1)
    finally:
        release_first.set()
        worker.cancel()
        with pytest.raises(asyncio.CancelledError):
            await worker

    assert responses[0]["request_id"] == "req_first"


@pytest.mark.asyncio
async def test_worker_cancels_in_flight_on_disconnect(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Disconnect cancels unfinished private requests before reconnecting."""
    started = asyncio.Event()
    cancelled = asyncio.Event()

    class Socket:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        def __aiter__(self):
            async def frames():
                yield json.dumps({
                    "type": "request", "request_id": "req_pending",
                    "method": "GET", "path": "/internal/api/v1/projects",
                })
                await asyncio.wait_for(started.wait(), timeout=1)
                # Simulate the WSS connection ending while HTTP is pending.
            return frames()

        async def send(self, value: str) -> None:
            raise AssertionError("Cancelled request must not send a response")

    async def forward(payload, client, key):
        started.set()
        try:
            await asyncio.Event().wait()
        finally:
            cancelled.set()

    async def stop_after_disconnect(delay):
        assert delay == 1
        raise asyncio.CancelledError

    monkeypatch.setattr(tunnel_worker, "connect", lambda *args, **kwargs: Socket())
    monkeypatch.setattr(tunnel_worker, "forward_request", forward)
    monkeypatch.setattr(tunnel_worker.asyncio, "sleep", stop_after_disconnect)
    with pytest.raises(asyncio.CancelledError):
        await asyncio.wait_for(
            tunnel_worker.run_worker(
                "wss://example.invalid/tunnel", "token", "http://bridge", "internal-key"
            ), timeout=2,
        )
    assert cancelled.is_set()
