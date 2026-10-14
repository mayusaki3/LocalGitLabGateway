"""Dedicated authentication for outbound reverse tunnel connections."""

from hmac import compare_digest


def is_valid_tunnel_bearer(header: str | None, expected_secret: str) -> bool:
    """Validate a tunnel-only Bearer credential without accepting API keys."""
    if not header or not expected_secret:
        return False
    scheme, separator, credential = header.partition(" ")
    if scheme != "Bearer" or separator != " " or not credential:
        return False
    if credential != credential.strip() or " " in credential:
        return False
    return compare_digest(credential.encode("utf-8"), expected_secret.encode("utf-8"))
