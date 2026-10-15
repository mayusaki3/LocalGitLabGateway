"""Canonical private project list endpoint tests without GitLab access."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from local_gitlab_gateway.private_bridge.canonical_projects import router


@pytest.mark.parametrize("page,per_page", [(1, 20), (2, 5)])
def test_canonical_projects(monkeypatch: pytest.MonkeyPatch, page: int, per_page: int) -> None:
    async def fake_fetch(**kwargs: object) -> list[dict]:
        assert kwargs["page"] == page
        assert kwargs["per_page"] == per_page
        return [{"id": 1, "name": "demo", "path": "demo"}]

    monkeypatch.setattr(
        "local_gitlab_gateway.private_bridge.canonical_projects.fetch_gitlab_projects",
        fake_fetch,
    )
    app = FastAPI()
    app.state.gitlab_base_url = "https://gitlab.invalid"
    app.state.gitlab_personal_access_token = "test-only"
    app.include_router(router)
    response = TestClient(app).get(
        f"/internal/api/v1/projects?page={page}&per_page={per_page}",
        headers={"X-Request-ID": "req_test"},
    )
    assert response.status_code == 200
    assert response.json()["projects"][0]["id"] == 1
