"""API key middleware."""

from collections.abc import Awaitable, Callable

from fastapi import Request
from starlette.responses import JSONResponse, Response


PUBLIC_EXCLUDED_PATHS = {
    "/health",
}

PRIVATE_EXCLUDED_PATHS = {
    "/internal/health",
}


async def public_api_key_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Validate public API key."""

    if request.url.path in PUBLIC_EXCLUDED_PATHS:
        return await call_next(request)

    request_id = getattr(request.state, "request_id", None)

    expected_api_key = getattr(request.app.state, "public_api_key", None)

    if not expected_api_key:
        return JSONResponse(
            status_code=500,
            content={
                "error": "public_api_key_not_configured",
                "request_id": request_id,
            },
        )

    provided_api_key = request.headers.get("X-API-Key")

    if provided_api_key != expected_api_key:
        return JSONResponse(
            status_code=401,
            content={
                "error": "invalid_api_key",
                "request_id": request_id,
            },
        )

    return await call_next(request)


async def internal_api_key_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Validate internal API key."""

    if request.url.path in PRIVATE_EXCLUDED_PATHS:
        return await call_next(request)

    request_id = getattr(request.state, "request_id", None)

    expected_api_key = getattr(request.app.state, "internal_api_key", None)

    if not expected_api_key:
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_api_key_not_configured",
                "request_id": request_id,
            },
        )

    provided_api_key = request.headers.get("X-Internal-API-Key")

    if provided_api_key != expected_api_key:
        return JSONResponse(
            status_code=401,
            content={
                "error": "invalid_internal_api_key",
                "request_id": request_id,
            },
        )

    return await call_next(request)
