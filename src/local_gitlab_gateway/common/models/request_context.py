"""Common request context models.

This module defines shared request tracking models.
"""

from pydantic import BaseModel, Field


class RequestContext(BaseModel):
    """Shared request context.

    Attributes:
        request_id: Unique request tracking identifier.
    """

    request_id: str = Field(..., pattern=r"^req_[a-zA-Z0-9_-]+$")
