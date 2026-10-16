"""GitLab project HTTP client tests without network access."""

import httpx
import pytest

from local_gitlab_gateway.private_bridge import gitlab_projects


@pytest.mark.asyncio
async def test_fetch_gitlab_projects(monkeypatch: pytest.MonkeyPatch) -> None:
    observed = {}

    def handler(request: httpx.Request) -> httpx.Response:
        observed["request"] = request
        return httpx.Response(200, json=[{"id": 17, "name": "demo"}])

    real_client = httpx.AsyncClient

    def fake_client(*args, **kwargs):
        observed["verify"] = kwargs.get("verify", True)
        return real_client(*args, transport=httpx.MockTransport(handler), **kwargs)

    monkeypatch.setattr(gitlab_projects.httpx, "AsyncClient", fake_client)
    result = await gitlab_projects.fetch_gitlab_projects(
        base_url="https://gitlab.invalid/",
        personal_access_token="test-only-pat",
        page=2,
        per_page=7,
        timeout_seconds=12,
    )
    assert result == [{"id": 17, "name": "demo"}]
    assert observed["verify"] is not False
    request = observed["request"]
    assert str(request.url).startswith("https://gitlab.invalid/api/v4/projects?")
    assert request.headers["private-token"] == "test-only-pat"
    assert request.url.params["page"] == "2"
    assert request.url.params["per_page"] == "7"
    assert request.url.params["membership"] == "true"
    assert request.url.params["simple"] == "true"


@pytest.mark.asyncio
async def test_fetch_gitlab_projects_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    real_client = httpx.AsyncClient

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, json={"message": "unavailable"})

    def fake_client(*args, **kwargs):
        return real_client(*args, transport=httpx.MockTransport(handler), **kwargs)

    monkeypatch.setattr(gitlab_projects.httpx, "AsyncClient", fake_client)
    with pytest.raises(httpx.HTTPStatusError):
        await gitlab_projects.fetch_gitlab_projects(
            base_url="https://gitlab.invalid",
            personal_access_token="test-only-pat",
        )
