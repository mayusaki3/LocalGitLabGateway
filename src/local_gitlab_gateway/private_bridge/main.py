"""Private Bridge Agent entrypoint.

This module provides the FastAPI application for the private bridge agent.
"""

from fastapi import FastAPI
import uvicorn

app = FastAPI(title="LocalGitLabGateway Private Bridge")


@app.get("/internal/health")
def health() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        dict[str, str]: Service status.
    """

    return {"status": "ok"}


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
