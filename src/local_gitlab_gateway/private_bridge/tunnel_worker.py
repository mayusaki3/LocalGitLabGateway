"""Manually started outbound WSS worker for the private network.

Start this process only during an authorized ChatGPT session. Stopping it
ends reconnection attempts; no persistent enable flag is stored.
"""

import asyncio
import json
import os
from typing import Any

import httpx
from pydantic import ValidationError
from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosed

from local_gitlab_gateway.common.tunnel_protocol import TunnelRequest, TunnelResponse
from local_gitlab_gateway.private_bridge.tunnel_client import forward_request


MAX_IN_FLIGHT = 16


def reconnect_delay(attempt: int) -> int:
    """Bounded exponential retry delay in seconds."""
    return min(30, 2 ** min(attempt, 5))


async def process_message(
    socket: Any,
    raw: str,
    client: httpx.AsyncClient,
    internal_api_key: str,
) -> None:
    """Handle one request and return a correlated, sanitized response."""
    try:
        payload = json.loads(raw)
        message = TunnelRequest.model_validate(payload)
    except (ValueError, ValidationError, TypeError):
        # Untrusted frames without a validated ID cannot be correlated.
        await socket.close(code=1008)
        return

    try:
        result = await forward_request(message.model_dump(), client, internal_api_key)
    except ValueError:
        result = TunnelResponse(
            request_id=message.request_id,
            status_code=403,
            body={
                "request_id": message.request_id,
                "error": {"code": "operation_denied", "message": "Operation denied"},
            },
        ).model_dump()
    except (httpx.HTTPError, httpx.TimeoutException):
        result = TunnelResponse(
            request_id=message.request_id,
            status_code=502,
            body={
                "request_id": message.request_id,
                "error": {"code": "private_bridge_unavailable",
                          "message": "Private bridge unavailable"},
            },
        ).model_dump()
    await socket.send(json.dumps(result, ensure_ascii=False))


async def run_worker(
    wss_url: str,
    tunnel_token: str,
    private_bridge_url: str,
    internal_api_key: str,
) -> None:
    """Connect outward until this explicitly started process is stopped."""
    if not wss_url.startswith("wss://"):
        raise ValueError("Tunnel endpoint must use wss://")
    if not all((tunnel_token, private_bridge_url, internal_api_key)):
        raise ValueError("Missing tunnel worker configuration")

    attempt = 0
    async with httpx.AsyncClient(base_url=private_bridge_url, timeout=30.0) as client:
        while True:
            try:
                async with connect(
                    wss_url,
                    additional_headers={"Authorization": f"Bearer {tunnel_token}"},
                    subprotocols=["lgg-tunnel.v1"],
                    max_size=1024 * 1024,
                ) as socket:
                    attempt = 0
                    in_flight: set[asyncio.Task[None]] = set()
                    try:
                        async for raw in socket:
                            while len(in_flight) >= MAX_IN_FLIGHT:
                                await asyncio.wait(
                                    in_flight, return_when=asyncio.FIRST_COMPLETED
                                )
                            task = asyncio.create_task(
                                process_message(socket, raw, client, internal_api_key)
                            )
                            in_flight.add(task)
                            task.add_done_callback(in_flight.discard)
                    finally:
                        for task in in_flight:
                            task.cancel()
                        if in_flight:
                            await asyncio.gather(*in_flight, return_exceptions=True)
            except (OSError, ConnectionClosed, TimeoutError):
                pass
            await asyncio.sleep(reconnect_delay(attempt))
            attempt += 1


def main() -> None:
    """Run only when an operator starts this worker process."""
    asyncio.run(run_worker(
        os.environ.get("LGG_TUNNEL_WSS_URL", ""),
        os.environ.get("LGG_TUNNEL_TOKEN", ""),
        os.environ.get("LGG_PRIVATE_BRIDGE_URL", ""),
        os.environ.get("LGG_INTERNAL_API_KEY", ""),
    ))


if __name__ == "__main__":
    main()
