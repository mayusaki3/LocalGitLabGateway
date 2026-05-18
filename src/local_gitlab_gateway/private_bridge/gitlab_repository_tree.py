"""GitLab repository tree client."""

from typing import Any

import httpx


async def fetch_repository_tree(
    *,
    gitlab_base_url: str,
    personal_access_token: str,
    project_id: int,
    path: str | None = None,
    ref: str | None = None,
    page: int = 1,
    per_page: int = 20,
    verify_tls: bool = True,
    timeout_seconds: int = 30,
) -> list[dict[str, Any]]:
    """Fetch repository tree from GitLab."""

    url = (
        f"{gitlab_base_url.rstrip('/')}"
        f"/api/v4/projects/{project_id}/repository/tree"
    )

    params: dict[str, Any] = {
        "page": page,
        "per_page": per_page,
    }

    if path:
        params["path"] = path

    if ref:
        params["ref"] = ref

    async with httpx.AsyncClient(
        verify=verify_tls,
        timeout=timeout_seconds,
    ) as client:
        response = await client.get(
            url,
            headers={
                "PRIVATE-TOKEN": personal_access_token,
            },
            params=params,
        )

        response.raise_for_status()

        return response.json()
