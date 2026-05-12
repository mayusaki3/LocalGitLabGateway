"""Public Gateway Service entrypoint.

This module provides the FastAPI application for the public gateway.
"""

from fastapi import FastAPI, Request
import uvicorn

from local_gitlab_gateway.common.middleware.request_id import request_id_middleware

app = FastAPI(title="LocalGitLabGateway Public Gateway")

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
