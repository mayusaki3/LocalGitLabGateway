"""Public Gateway Service entrypoint.

This module provides the FastAPI application for the public gateway.
"""

from fastapi import FastAPI, Request
import uvicorn

from local_gitlab_gateway.common.config import load_public_gateway_config
from local_gitlab_gateway.common.middleware.api_key import (
    public_api_key_middleware,
)
from local_gitlab_gateway.common.middleware.request_id import request_id_middleware

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
