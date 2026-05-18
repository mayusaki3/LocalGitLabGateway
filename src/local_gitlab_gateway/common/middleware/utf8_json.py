"""UTF-8 JSON response middleware."""

from starlette.middleware.base import BaseHTTPMiddleware


class Utf8JsonMiddleware(BaseHTTPMiddleware):
    """Force UTF-8 charset for JSON responses."""

    async def dispatch(self, request, call_next):
        response = await call_next(request)

        content_type = response.headers.get(
            "content-type",
            "",
        )

        if (
            content_type.startswith("application/json")
            and "charset=" not in content_type
        ):
            response.headers["content-type"] = (
                "application/json; charset=utf-8"
            )

        return response
