"""Canonical public API backed by the on-demand tunnel."""

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse

from local_gitlab_gateway.common.request_id import generate_request_id
from local_gitlab_gateway.common.tunnel_relay import TunnelDisconnected, TunnelTimeout
from local_gitlab_gateway.public_gateway.tunnel_endpoint import session

router = APIRouter()


@router.get("/api/v1/projects")
async def list_projects(
    request: Request,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
) -> JSONResponse:
    """Forward the validated project list request through the active tunnel."""
    request_id = getattr(request.state, "request_id", None) or generate_request_id()
    try:
        result = await session.request(
            request_id,
            "GET",
            "/internal/api/v1/projects",
            query={"page": page, "per_page": per_page},
        )
    except TunnelDisconnected:
        return JSONResponse(
            status_code=503,
            content={"request_id": request_id,
                     "error": {"code": "tunnel_unavailable",
                               "message": "Tunnel unavailable"}},
        )
    except TunnelTimeout:
        return JSONResponse(
            status_code=504,
            content={"request_id": request_id,
                     "error": {"code": "tunnel_timeout",
                               "message": "Tunnel request timed out"}},
        )
    return JSONResponse(status_code=result.status_code, content=result.body)
