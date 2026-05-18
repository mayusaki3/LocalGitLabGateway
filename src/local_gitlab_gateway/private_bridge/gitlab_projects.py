"""GitLab project API client."""

from typing import Any

import httpx


async def fetch_gitlab_projects(
    *,
    base_url: str,
    personal_access_token: str,
    page: int = 1,
    per_page: int = 20,
    timeout_seconds: int = 30,
) -> list[dict[str, Any]]:
    """Fetch GitLab projects.

    Args:
        base_url: GitLab base URL.
        personal_access_token: GitLab PAT.
        page: Pagination page.
        per_page: Items per page.
        timeout_seconds: HTTP timeout.

    Returns:
        GitLab project list.

    Raises:
        httpx.HTTPError: HTTP communication failure.
    """

    url = f"{base_url.rstrip('/')}/api/v4/projects"

    async with httpx.AsyncClient(
        timeout=timeout_seconds,
        verify=False,
    ) as client:
        response = await client.get(
            url,
            headers={
                "PRIVATE-TOKEN": personal_access_token,
            },
            params={
                "page": page,
                "per_page": per_page,
                "membership": "true",
                "simple": "true",
            },
        )

        response.raise_for_status()

        return response.json()
