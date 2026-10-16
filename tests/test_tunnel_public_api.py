"""Public API behavior while using the tunnel."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from local_gitlab_gateway.public_gateway.tunnel_api import router
from local_gitlab_gateway.public_gateway.tunnel_endpoint import session


def test_disconnected_returns_503() -> None:
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    response = client.get("/api/v1/projects")
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "tunnel_unavailable"
    assert response.json()["request_id"].startswith("req_")


def test_health_not_dependent_on_tunnel() -> None:
    assert session.socket is None


def test_tunnel_timeout_returns_504(monkeypatch) -> None:
    from local_gitlab_gateway.common.tunnel_relay import TunnelTimeoutError

    async def fail(*args, **kwargs):
        raise TunnelTimeoutError("timeout")

    monkeypatch.setattr(session, "request", fail)
    app = FastAPI()
    app.include_router(router)
    response = TestClient(app).get("/api/v1/projects")
    assert response.status_code == 504
    assert response.json()["error"]["code"] == "tunnel_timeout"


def test_tunnel_response_is_forwarded(monkeypatch) -> None:
    from local_gitlab_gateway.common.tunnel_protocol import TunnelResponse

    async def succeed(request_id, method, path, query):
        assert method == "GET"
        assert path == "/internal/api/v1/projects"
        assert query == {"page": 2, "per_page": 5}
        return TunnelResponse(
            request_id=request_id,
            status_code=200,
            body={"request_id": request_id, "projects": [{"id": 7}]},
        )

    monkeypatch.setattr(session, "request", succeed)
    app = FastAPI()
    app.include_router(router)
    response = TestClient(app).get("/api/v1/projects?page=2&per_page=5")
    assert response.status_code == 200
    assert response.json()["projects"] == [{"id": 7}]
