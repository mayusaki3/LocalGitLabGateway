"""Canonical Private Bridge project API."""

import httpx
from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse

from local_gitlab_gateway.common.request_id import generate_request_id
from local_gitlab_gateway.private_bridge.gitlab_projects import fetch_gitlab_projects

router = APIRouter()


@router.get("/internal/api/v1/projects")
async def list_projects(
    request: Request,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
) -> JSONResponse:
    """Return normalized GitLab projects without exposing the PAT."""
    request_id = getattr(request.state, "request_id", None)
    if request_id is None:
        request_id = request.headers.get("X-Request-ID") or generate_request_id()
    try:
        projects = await fetch_gitlab_projects(
            base_url=request.app.state.gitlab_base_url,
            personal_access_token=request.app.state.gitlab_personal_access_token,
            page=page,
            per_page=per_page,
        )
    except httpx.HTTPError:
        return JSONResponse(
            status_code=502,
            content={"request_id": request_id,
                     "error": {"code": "gitlab_unavailable",
                               "message": "GitLab request failed"}},
        )
    return JSONResponse(
        content={"request_id": request_id, "projects": projects},
    )
