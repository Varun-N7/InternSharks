import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class RequestTrackingMiddleware(
    BaseHTTPMiddleware
):
    async def dispatch(
        self,
        request: Request,
        call_next,
    ):
        request_id = request.headers.get(
            "X-Request-ID"
        )

        if not request_id:
            request_id = (
                f"req_{uuid.uuid4().hex}"
            )

        request.state.request_id = request_id

        response = await call_next(request)

        response.headers[
            "X-Request-ID"
        ] = request_id

        return response