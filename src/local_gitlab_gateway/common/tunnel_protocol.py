"""Strict message schemas for the reverse WebSocket tunnel."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TunnelRequest(BaseModel):
    """Request forwarded to the private bridge."""

    model_config = ConfigDict(extra="forbid", strict=True)

    type: Literal["request"] = "request"
    request_id: str = Field(pattern=r"^req_[A-Za-z0-9_-]+$", max_length=128)
    method: Literal["GET", "POST", "PUT"]
    path: str
    query: dict[str, Any] = Field(default_factory=dict)
    body: Any = None

    @model_validator(mode="after")
    def validate_path(self) -> "TunnelRequest":
        path = self.path
        if (
            not path.startswith("/internal/api/v1/projects")
            or (len(path) > len("/internal/api/v1/projects")
                and path[len("/internal/api/v1/projects")] != "/")
            or path.startswith("//")
            or "?" in path
            or "#" in path
            or "\\" in path
            or any(segment in (".", "..") for segment in path.split("/"))
        ):
            raise ValueError("Invalid internal API path")
        return self


class TunnelResponse(BaseModel):
    """Response paired with a previously forwarded request."""

    model_config = ConfigDict(extra="forbid", strict=True)

    type: Literal["response"] = "response"
    request_id: str = Field(pattern=r"^req_[A-Za-z0-9_-]+$", max_length=128)
    status_code: int = Field(ge=100, le=599)
    body: dict[str, Any]

    @model_validator(mode="after")
    def validate_request_id(self) -> "TunnelResponse":
        if self.body.get("request_id") != self.request_id:
            raise ValueError("Response request_id mismatch")
        return self
