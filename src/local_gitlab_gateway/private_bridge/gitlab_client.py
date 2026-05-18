"""GitLab API client utilities."""

from typing import Any

import httpx


async def fetch_gitlab_version(
    *,
    base_url: str,
    personal_access_token: str,
    timeout_seconds: int = 30,
) -> dict[str, Any]:
    """Fetch GitLab version information.

    Args:
        base_url: GitLab base URL.
        personal_access_token: GitLab PAT.
        timeout_seconds: HTTP timeout.

    Returns:
        GitLab version response.

    Raises:
        httpx.HTTPError: HTTP communication failure.
    """

    url = f"{base_url.rstrip('/')}/api/v4/version"

    async with httpx.AsyncClient(
        timeout=timeout_seconds,
        verify=False,
    ) as client:
        response = await client.get(
            url,
            headers={
                "PRIVATE-TOKEN": personal_access_token,
            },
        )

        response.raise_for_status()

        return response.json()
