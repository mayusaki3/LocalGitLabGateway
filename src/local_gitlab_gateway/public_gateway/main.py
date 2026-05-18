"""Public Gateway Service entrypoint.

This module provides the FastAPI application for the public gateway.
"""

from fastapi import FastAPI, HTTPException, Query, Request
import httpx
import uvicorn

from local_gitlab_gateway.common.config import load_public_gateway_config
from local_gitlab_gateway.common.middleware.api_key import (
    public_api_key_middleware,
)
from local_gitlab_gateway.common.middleware.request_id import request_id_middleware
from local_gitlab_gateway.public_gateway.private_bridge_client import (
    fetch_projects_via_private_bridge,
)
from local_gitlab_gateway.public_gateway.private_bridge_repository_tree import (
    fetch_repository_tree_via_private_bridge,
)

runtime_config = load_public_gateway_config()

app = FastAPI(title="LocalGitLabGateway Public Gateway")

app.state.public_api_key = runtime_config["security"]["api_key"]
app.state.private_bridge_base_url = runtime_config["private_bridge"]["base_url"]
app.state.internal_api_key = runtime_config["private_bridge"][
    "internal_api_key"
]

app.middleware("http")(public_api_key_middleware)
app.middleware("http")(request_id_middleware)


@app.get("/health")
def health(request: Request) -> dict[str, str]:
    """Health check endpoint.

    Args:
        request: FastAPI request.

    Returns:
        dict[str, str]: Service status and request ID.
    """

    return {
        "status": "ok",
        "request_id": request.state.request_id,
    }


@app.get("/v1/config-check")
def config_check(request: Request) -> dict[str, str]:
    """Configuration check endpoint."""

    return {
        "status": "ok",
        "request_id": request.state.request_id,
        "private_bridge_base_url": app.state.private_bridge_base_url,
    }


@app.get("/v1/gitlab/projects")
async def gitlab_projects(
    request: Request,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
) -> dict:
    """Fetch GitLab projects through private bridge."""

    try:
        projects_response = await fetch_projects_via_private_bridge(
            private_bridge_base_url=app.state.private_bridge_base_url,
            internal_api_key=app.state.internal_api_key,
            page=page,
            per_page=per_page,
        )

    except httpx.HTTPError as exception:
        raise HTTPException(
            status_code=502,
            detail={
                "error": "private_bridge_request_failed",
                "message": str(exception),
                "request_id": request.state.request_id,
            },
        ) from exception

    return {
        "status": "ok",
        "request_id": request.state.request_id,
        "private_bridge": projects_response,
    }


@app.get(
    "/v1/gitlab/projects/{project_id}/repository/tree"
)
async def repository_tree(
    request: Request,
    project_id: int,
    path: str | None = None,
    ref: str | None = None,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
) -> dict:
    """Fetch repository tree through private bridge."""

    try:
        tree_response = await fetch_repository_tree_via_private_bridge(
            private_bridge_base_url=app.state.private_bridge_base_url,
            internal_api_key=app.state.internal_api_key,
            project_id=project_id,
            path=path,
            ref=ref,
            page=page,
            per_page=per_page,
        )

    except httpx.HTTPError as exception:
        raise HTTPException(
            status_code=502,
            detail={
                "error": "private_bridge_request_failed",
                "message": str(exception),
                "request_id": request.state.request_id,
            },
        ) from exception

    return {
        "status": "ok",
        "request_id": request.state.request_id,
        "private_bridge": tree_response,
    }


def run() -> None:
    """Run the Public Gateway Service."""

    uvicorn.run(
        "local_gitlab_gateway.public_gateway.main:app",
        host="0.0.0.0",
        port=8080,
        reload=False,
    )


if __name__ == "__main__":
    run()
