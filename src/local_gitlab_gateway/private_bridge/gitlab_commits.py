"""GitLab commits API client."""

from typing import Any

import httpx


async def fetch_gitlab_commits(
    gitlab_base_url: str,
    personal_access_token: str,
    project_id: int,
    ref_name: str | None,
    page: int,
    per_page: int,
    verify_tls: bool,
) -> list[dict[str, Any]]:
    """Fetch GitLab commits."""

    api_url = (
        f"{gitlab_base_url}/api/v4/projects/"
        f"{project_id}/repository/commits"
    )

    headers = {
        "PRIVATE-TOKEN": personal_access_token,
    }

    params = {
        "page": page,
        "per_page": per_page,
    }

    if ref_name:
        params["ref_name"] = ref_name

    async with httpx.AsyncClient(
        verify=verify_tls,
        timeout=30.0,
    ) as client:
        response = await client.get(
            api_url,
            headers=headers,
            params=params,
        )

        response.raise_for_status()

        return response.json()
