from typing import Any

import httpx


async def fetch_repository_tree_via_private_bridge(
    *,
    private_bridge_base_url: str,
    internal_api_key: str,
    project_id: int,
    path: str | None = None,
    ref: str | None = None,
    page: int = 1,
    per_page: int = 20,
    timeout_seconds: int = 30,
) -> dict[str, Any]:
    url = (
        f"{private_bridge_base_url.rstrip('/')}"
        f"/internal/gitlab/projects/{project_id}/repository/tree"
    )

    params: dict[str, Any] = {
        "page": page,
        "per_page": per_page,
    }

    if path:
        params["path"] = path

    if ref:
        params["ref"] = ref

    async with httpx.AsyncClient(timeout=timeout_seconds) as client:
        response = await client.get(
            url,
            headers={
                "X-Internal-API-Key": internal_api_key,
            },
            params=params,
        )

        response.raise_for_status()

        return response.json()
