"""Forward validated tunnel requests to the local private bridge API."""

import re
from typing import Any

import httpx

from local_gitlab_gateway.common.tunnel_protocol import TunnelRequest, TunnelResponse

_ALLOWED = (
    ("GET", re.compile(r"^/internal/api/v1/projects$")),
    ("GET", re.compile(r"^/internal/api/v1/projects/[0-9]+/branches$")),
    ("GET", re.compile(r"^/internal/api/v1/projects/[0-9]+/files/.+$")),
    ("POST", re.compile(r"^/internal/api/v1/projects/[0-9]+/files/.+$")),
    ("PUT", re.compile(r"^/internal/api/v1/projects/[0-9]+/files/.+$")),
    ("POST", re.compile(r"^/internal/api/v1/projects/[0-9]+/merge-requests$")),
    ("POST", re.compile(r"^/internal/api/v1/projects/[0-9]+/issues$")),
)


async def forward_request(
    payload: dict[str, Any],
    client: httpx.AsyncClient,
    internal_api_key: str,
) -> dict[str, Any]:
    """Forward only documented operations; never accept arbitrary target URLs."""
    message = TunnelRequest.model_validate(payload)
    if not any(
        method == message.method and pattern.fullmatch(message.path)
        for method, pattern in _ALLOWED
    ):
        raise ValueError("Operation not allowed")
    response = await client.request(
        message.method,
        message.path,
        params=message.query,
        json=message.body if message.method != "GET" else None,
        headers={
            "Authorization": f"Bearer {internal_api_key}",
            "X-Request-ID": message.request_id,
        },
    )
    body = response.json()
    if not isinstance(body, dict) or body.get("request_id") != message.request_id:
        raise ValueError("Invalid private bridge response")
    return TunnelResponse(
        request_id=message.request_id,
        status_code=response.status_code,
        body=body,
    ).model_dump()
