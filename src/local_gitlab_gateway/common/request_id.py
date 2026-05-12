"""Request ID utilities.

This module provides request tracking ID generation for API calls.
"""

from uuid import uuid4


def generate_request_id() -> str:
    """Generate a request ID.

    Returns:
        str: Request ID with the `req_` prefix.
    """

    return f"req_{uuid4().hex}"
