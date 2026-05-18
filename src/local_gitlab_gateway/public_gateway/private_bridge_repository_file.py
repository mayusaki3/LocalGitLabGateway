from typing import Any

import httpx


async def fetch_repository_file_via_private_bridge(
    *,
    private_bridge_base_url: str,
    internal_api_key: str,
    project_id: int,
    file_path: str,
    ref: str = "HEAD",
    timeout_seconds: int = 30,
) -> dict[str, Any]:
    url = (
        f"{private_bridge_base_url.rstrip('/')}"
        f"/internal/gitlab/projects/{project_id}/repository/files/{file_path}"
    )

    async with httpx.AsyncClient(timeout=timeout_seconds) as client:
        response = await client.get(
            url,
            headers={
                "X-Internal-API-Key": internal_api_key,
            },
            params={
                "ref": ref,
            },
        )

        response.raise_for_status()

        return response.json()
