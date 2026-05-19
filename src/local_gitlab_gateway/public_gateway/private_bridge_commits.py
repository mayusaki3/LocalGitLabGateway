"""Private Bridge commits client."""

from typing import Any

import httpx


async def fetch_commits_via_private_bridge(
    private_bridge_base_url: str,
    internal_api_key: str,
    project_id: int,
    ref_name: str | None,
    page: int,
    per_page: int,
) -> dict[str, Any]:
    """Fetch commits through private bridge."""

    endpoint = (
        f"{private_bridge_base_url}/internal/gitlab/projects/"
        f"{project_id}/commits"
    )

    headers = {
        "X-Internal-API-Key": internal_api_key,
    }

    params = {
        "page": page,
        "per_page": per_page,
    }

    if ref_name:
        params["ref_name"] = ref_name

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            endpoint,
            headers=headers,
            params=params,
        )

        response.raise_for_status()

        return response.json()
