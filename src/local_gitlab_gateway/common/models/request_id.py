"""Request ID utility.

This module provides request ID generation utilities shared across
Public Gateway Service and Private Bridge Agent.
"""

from uuid import uuid4


REQUEST_ID_PREFIX = "req_"


def generate_request_id() -> str:
    """Generate a request identifier.

    Returns:
        Generated request ID.
    """
    return f"{REQUEST_ID_PREFIX}{uuid4().hex}"
