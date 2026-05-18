"""GitLab repository file client."""

from urllib.parse import quote

import httpx


async def fetch_repository_file(
    *,
    gitlab_base_url: str,
    personal_access_token: str,
    project_id: int,
    file_path: str,
    ref: str = "HEAD",
    verify_tls: bool = True,
    timeout_seconds: int = 30,
) -> str:
    """Fetch repository file content from GitLab."""

    encoded_file_path = quote(file_path, safe="")

    url = (
        f"{gitlab_base_url.rstrip('/')}"
        f"/api/v4/projects/{project_id}/repository/files/"
        f"{encoded_file_path}/raw"
    )

    async with httpx.AsyncClient(
        verify=verify_tls,
        timeout=timeout_seconds,
    ) as client:
        response = await client.get(
            url,
            headers={
                "PRIVATE-TOKEN": personal_access_token,
            },
            params={
                "ref": ref,
            },
        )

        response.raise_for_status()

        return response.text
