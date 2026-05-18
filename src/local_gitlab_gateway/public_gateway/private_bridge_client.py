"""Private bridge API client."""

from typing import Any

import httpx


async def fetch_projects_via_private_bridge(
    *,
    private_bridge_base_url: str,
    internal_api_key: str,
    page: int = 1,
    per_page: int = 20,
    timeout_seconds: int = 30,
) -> dict[str, Any]:
    """Fetch GitLab projects through private bridge."""

    url = (
        f"{private_bridge_base_url.rstrip('/')}"
        "/internal/gitlab/projects"
    )

    async with httpx.AsyncClient(timeout=timeout_seconds) as client:
        response = await client.get(
            url,
            headers={
                "X-Internal-API-Key": internal_api_key,
            },
            params={
                "page": page,
                "per_page": per_page,
            },
        )

        response.raise_for_status()

        return response.json()
