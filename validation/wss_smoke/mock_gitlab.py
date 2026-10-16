"""Local-only mock GitLab API for the manual WSS smoke test.

Run with uvicorn bound to 127.0.0.1; never deploy this fixture.
"""

from fastapi import FastAPI, Header, HTTPException, Query

app = FastAPI(title="LGG mock GitLab")


@app.get("/api/v4/projects")
def projects(
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
    return [{"id": 42, "name": "mock-project", "page": page, "per_page": per_page}]
