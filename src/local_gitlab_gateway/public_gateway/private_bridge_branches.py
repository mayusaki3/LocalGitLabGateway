"""Private Bridge branches client."""

from typing import Any

import httpx


async def fetch_branches_via_private_bridge(
    private_bridge_base_url: str,
    internal_api_key: str,
    project_id: int,
    page: int,
    per_page: int,
) -> dict[str, Any]:
    """Fetch branches through private bridge."""

    endpoint = (
        f"{private_bridge_base_url}/internal/gitlab/projects/"
        f"{project_id}/branches"
    )

    headers = {
        "X-Internal-API-Key": internal_api_key,
    }

    params = {
        "page": page,
        "per_page": per_page,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            endpoint,
            headers=headers,
            params=params,
        )

        response.raise_for_status()

        return response.json()
