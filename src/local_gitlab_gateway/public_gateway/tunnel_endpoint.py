"""Authenticated WebSocket ingress for the outbound private bridge tunnel."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from local_gitlab_gateway.common.tunnel_auth import is_valid_tunnel_bearer
from local_gitlab_gateway.common.tunnel_protocol import TunnelResponse
from local_gitlab_gateway.common.tunnel_session import TunnelSession

router = APIRouter()
session = TunnelSession()


@router.websocket("/internal/tunnel/v1")
async def tunnel_ingress(websocket: WebSocket) -> None:
    """Accept one authenticated tunnel, rejecting unsolicited frames."""
    secret = getattr(websocket.app.state, "tunnel_token", "")
    if not is_valid_tunnel_bearer(websocket.headers.get("authorization"), secret):
        await websocket.close(code=1008)
        return
    if "lgg-tunnel.v1" not in websocket.scope.get("subprotocols", []):
        await websocket.close(code=1002)
        return
    if not session.attach(websocket):
        await websocket.close(code=1013)
        return
    try:
        await websocket.accept(subprotocol="lgg-tunnel.v1")
        while True:
            payload = await websocket.receive_json()
            try:
                TunnelResponse.model_validate(payload)
            except ValidationError:
                await websocket.close(code=1008)
                break
            # No request dispatcher is connected yet; responses are not processed.
    except WebSocketDisconnect:
        pass
    finally:
        session.detach(websocket)
