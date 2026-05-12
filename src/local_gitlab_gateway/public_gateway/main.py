"""Public Gateway Service entrypoint.

This module provides the FastAPI application for the public gateway.
"""

from fastapi import FastAPI
import uvicorn

app = FastAPI(title="LocalGitLabGateway Public Gateway")


@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        dict[str, str]: Service status.
    """

    return {"status": "ok"}


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
