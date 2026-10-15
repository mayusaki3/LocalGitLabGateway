"""In-memory request correlation for one active tunnel connection."""

import asyncio
from typing import Any

from local_gitlab_gateway.common.tunnel_protocol import TunnelRequest, TunnelResponse


class TunnelDisconnectedError(RuntimeError):
    """No usable tunnel connection."""


class TunnelTimeoutError(RuntimeError):
    """No response arrived before the deadline."""


class TunnelRelay:
    def __init__(self, timeout: float = 30.0) -> None:
        self.timeout = timeout
        self.socket: Any | None = None
        self.pending: dict[str, asyncio.Future[TunnelResponse]] = {}
        self.send_lock = asyncio.Lock()

    @property
    def connected(self) -> bool:
        return self.socket is not None

    def attach(self, socket: Any) -> bool:
        if self.socket is not None:
            return False
        self.socket = socket
        return True

    def detach(self, socket: Any) -> None:
        if self.socket is not socket:
            return
        self.socket = None
        for future in self.pending.values():
            if not future.done():
                future.set_exception(TunnelDisconnectedError("Tunnel disconnected"))
        self.pending.clear()

    async def request(
        self,
        request_id: str,
        method: str,
        path: str,
        query: dict[str, Any] | None = None,
        body: Any = None,
    ) -> TunnelResponse:
        message = TunnelRequest(
            request_id=request_id,
            method=method,
            path=path,
            query=query or {},
            body=body,
        )
        if self.socket is None:
            raise TunnelDisconnectedError("Tunnel unavailable")
        if request_id in self.pending:
            raise ValueError("Duplicate pending request_id")
        loop = asyncio.get_running_loop()
        future: asyncio.Future[TunnelResponse] = loop.create_future()
        self.pending[request_id] = future
        try:
            async with self.send_lock:
                if self.socket is None:
                    raise TunnelDisconnectedError("Tunnel disconnected")
                await self.socket.send_json(message.model_dump())
            try:
                return await asyncio.wait_for(future, timeout=self.timeout)
            except TimeoutError as exc:
                raise TunnelTimeoutError("Tunnel request timed out") from exc
        finally:
            self.pending.pop(request_id, None)

    def resolve(self, payload: dict[str, Any]) -> bool:
        response = TunnelResponse.model_validate(payload)
        future = self.pending.get(response.request_id)
        if future is None or future.done():
            return False
        future.set_result(response)
        return True
