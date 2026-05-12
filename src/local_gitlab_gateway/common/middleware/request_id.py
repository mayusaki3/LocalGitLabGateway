"""Request ID middleware.

This middleware assigns a request ID to every HTTP request.
"""

from collections.abc import Awaitable, Callable

from fastapi import Request, Response

from local_gitlab_gateway.common.request_id import generate_request_id


async def request_id_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Attach a request ID to the request and response.

    Args:
        request: Incoming HTTP request.
        call_next: Next ASGI handler.

    Returns:
        Response: HTTP response with request ID header.
    """

    request_id = generate_request_id()

    request.state.request_id = request_id

    response = await call_next(request)

    response.headers["X-Request-ID"] = request_id

    return response
