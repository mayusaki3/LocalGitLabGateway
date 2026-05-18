"""Private Bridge Agent entrypoint.

This module provides the FastAPI application for the private bridge agent.
"""

from fastapi import FastAPI, Request
import uvicorn

from local_gitlab_gateway.common.config import load_private_bridge_config
from local_gitlab_gateway.common.middleware.api_key import (
    internal_api_key_middleware,
)
from local_gitlab_gateway.common.middleware.request_id import request_id_middleware

runtime_config = load_private_bridge_config()

app = FastAPI(title="LocalGitLabGateway Private Bridge")

app.state.internal_api_key = runtime_config["security"][
    "internal_api_key"
]
app.state.gitlab_base_url = runtime_config["gitlab"]["base_url"]

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
