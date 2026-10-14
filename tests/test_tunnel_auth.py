"""Authentication tests for the dedicated tunnel credential."""

import pytest

from local_gitlab_gateway.common.tunnel_auth import is_valid_tunnel_bearer


@pytest.mark.parametrize(
    ("header", "expected"),
    [
        ("Bearer tunnel-secret", True),
        ("Bearer wrong-secret", False),
        ("Basic tunnel-secret", False),
        ("bearer tunnel-secret", False),
        ("Bearer ", False),
        ("Bearer tunnel-secret extra", False),
        ("", False),
        (None, False),
    ],
)
def test_tunnel_bearer_authentication(header: str | None, expected: bool) -> None:
    assert is_valid_tunnel_bearer(header, "tunnel-secret") is expected


def test_missing_server_secret_fails_closed() -> None:
    assert not is_valid_tunnel_bearer("Bearer tunnel-secret", "")


def test_reject_public_api_key_as_tunnel_credential() -> None:
    assert not is_valid_tunnel_bearer("Bearer public-api-key", "tunnel-secret")
