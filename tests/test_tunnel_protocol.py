"""Protocol validation tests for the reverse WebSocket tunnel."""

import pytest
from pydantic import ValidationError

from local_gitlab_gateway.common.tunnel_protocol import TunnelRequest, TunnelResponse


def test_valid_request() -> None:
    message = TunnelRequest(
        request_id="req_123",
        method="GET",
        path="/internal/api/v1/projects",
        query={},
        body=None,
    )
    assert message.type == "request"
    assert message.request_id == "req_123"


@pytest.mark.parametrize("path", [
    "https://example.com/path",
    "//example.com/path",
    "/internal/api/v1/../admin",
    "/internal/api/v1/projects#fragment",
    "/other/path",
])
def test_reject_unsafe_path(path: str) -> None:
    with pytest.raises(ValidationError):
        TunnelRequest(request_id="req_123", method="GET", path=path)


def test_reject_unapproved_method() -> None:
    with pytest.raises(ValidationError):
        TunnelRequest(request_id="req_123", method="DELETE", path="/internal/api/v1/projects")


def test_reject_invalid_request_id() -> None:
    with pytest.raises(ValidationError):
        TunnelRequest(request_id="invalid", method="GET", path="/internal/api/v1/projects")


def test_response_request_id_consistency() -> None:
    message = TunnelResponse(
        request_id="req_123",
        status_code=200,
        body={"request_id": "req_123", "projects": []},
    )
    assert message.type == "response"
    with pytest.raises(ValidationError):
        TunnelResponse(
            request_id="req_123",
            status_code=200,
            body={"request_id": "req_other"},
        )


def test_reject_extra_fields() -> None:
    with pytest.raises(ValidationError):
        TunnelRequest(
            request_id="req_123",
            method="GET",
            path="/internal/api/v1/projects",
            host="example.com",
        )
