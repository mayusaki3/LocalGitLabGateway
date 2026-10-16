"""Local-only mock GitLab API for the manual WSS smoke test.

Run with uvicorn bound to 127.0.0.1; never deploy this fixture.
"""

import asyncio

from fastapi import FastAPI, Header, HTTPException, Query

app = FastAPI(title="LGG mock GitLab")


@app.get("/api/v4/projects")
async def projects(
    private_token: str | None = Header(default=None),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1),
    membership: bool = True,
    simple: bool = True,
) -> list[dict[str, object]]:
    if private_token != "local-mock-pat":
        raise HTTPException(status_code=401, detail="invalid mock PAT")
    if not membership or not simple:
        raise HTTPException(status_code=400, detail="expected GitLab filters")
    # Opt-in delay for a deterministic in-flight tunnel disconnect test.
    # page=99 is reserved for local validation; regular requests stay fast.
    if page == 99:
        await asyncio.sleep(10)
    return [{"id": 42, "name": "mock-project", "page": page, "per_page": per_page}]
