"""Private Bridge Agent entrypoint.

This module provides the FastAPI application for the private bridge agent.
"""

from fastapi import FastAPI, HTTPException, Query, Request
import httpx
import uvicorn

from local_gitlab_gateway.common.config import load_private_bridge_config
from local_gitlab_gateway.common.middleware.api_key import (
    internal_api_key_middleware,
)
from local_gitlab_gateway.common.middleware.request_id import request_id_middleware
from local_gitlab_gateway.private_bridge.gitlab_client import (
    fetch_gitlab_version,
)
from local_gitlab_gateway.private_bridge.gitlab_projects import (
    fetch_gitlab_projects,
)

runtime_config = load_private_bridge_config()

app = FastAPI(title="LocalGitLabGateway Private Bridge")

app.state.internal_api_key = runtime_config["security"][
    "internal_api_key"
]
app.state.gitlab_base_url = runtime_config["gitlab"]["base_url"]
app.state.gitlab_personal_access_token = runtime_config["gitlab"][
    "personal_access_token"
]

app.middleware("http")(internal_api_key_middleware)
app.middleware("http")(request_id_middleware)


@app.get("/internal/health")
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


@app.get("/internal/config-check")
def config_check(request: Request) -> dict[str, str]:
    """Configuration check endpoint."""

    return {
        "status": "ok",
        "request_id": request.state.request_id,
        "gitlab_base_url": app.state.gitlab_base_url,
    }


@app.get("/internal/gitlab/version")
async def gitlab_version(request: Request) -> dict:
    """Fetch GitLab version information."""

    try:
        version_response = await fetch_gitlab_version(
            base_url=app.state.gitlab_base_url,
            personal_access_token=app.state.gitlab_personal_access_token,
        )

    except httpx.HTTPError as exception:
        raise HTTPException(
            status_code=502,
            detail={
                "error": "gitlab_request_failed",
                "message": str(exception),
                "request_id": request.state.request_id,
            },
        ) from exception

    return {
        "status": "ok",
        "request_id": request.state.request_id,
        "gitlab": version_response,
    }


@app.get("/internal/gitlab/projects")
async def gitlab_projects(
    request: Request,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
) -> dict:
    """Fetch GitLab projects."""

    try:
        projects = await fetch_gitlab_projects(
            base_url=app.state.gitlab_base_url,
            personal_access_token=app.state.gitlab_personal_access_token,
            page=page,
            per_page=per_page,
        )

    except httpx.HTTPError as exception:
        raise HTTPException(
            status_code=502,
            detail={
                "error": "gitlab_request_failed",
                "message": str(exception),
                "request_id": request.state.request_id,
            },
        ) from exception

    return {
        "status": "ok",
        "request_id": request.state.request_id,
        "page": page,
        "per_page": per_page,
        "projects": projects,
    }


def run() -> None:
    """Run the Private Bridge Agent."""

    uvicorn.run(
        "local_gitlab_gateway.private_bridge.main:app",
        host="0.0.0.0",
        port=8081,
        reload=False,
    )


if __name__ == "__main__":
    run()
