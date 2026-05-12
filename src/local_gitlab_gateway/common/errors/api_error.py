"""Common API error models.

This module defines standardized API error responses.
"""

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Error detail payload.

    Attributes:
        code: Machine readable error code.
        message: Human readable error message.
    """

    code: str
    message: str


class ErrorResponse(BaseModel):
    """Standard API error response.

    Attributes:
        request_id: Request tracking ID.
        error: Error detail.
    """

    request_id: str
    error: ErrorDetail
