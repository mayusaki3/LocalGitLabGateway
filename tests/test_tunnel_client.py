"""Private-side tunnel request forwarding tests."""

import httpx
import pytest

from local_gitlab_gateway.private_bridge.tunnel_client import forward_request


@pytest.mark.asyncio
async def test_forward_project_list() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/internal/api/v1/projects"
        assert request.headers["authorization"] == "Bearer internal-secret"
        assert request.headers["x-request-id"] == "req_one"
        return httpx.Response(200, json={"request_id": "req_one", "projects": []})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://bridge") as client:
        response = await forward_request(
            {"type": "request", "request_id": "req_one", "method": "GET",
             "path": "/internal/api/v1/projects", "query": {}, "body": None},
            client, "internal-secret",
        )
    assert response["status_code"] == 200
    assert response["body"]["request_id"] == "req_one"


@pytest.mark.asyncio
async def test_reject_unapproved_route() -> None:
    async with httpx.AsyncClient(base_url="http://bridge") as client:
        with pytest.raises(ValueError):
            await forward_request(
                {"type": "request", "request_id": "req_one", "method": "GET",
                 "path": "/internal/api/v1/projects/1/secret"},
                client, "internal-secret",
            )
