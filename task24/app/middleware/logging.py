import time

from starlette.middleware.base import (
    BaseHTTPMiddleware,
)

from app.observability.logging import logger


class RequestLoggingMiddleware(
    BaseHTTPMiddleware
):
    async def dispatch(
        self,
        request,
        call_next,
    ):
        started = time.perf_counter()

        response = None

        try:
            response = await call_next(
                request
            )
            return response

        finally:
            latency_ms = round(
                (
                    time.perf_counter()
                    - started
                )
                * 1000,
                3,
            )

            request_id = getattr(
                request.state,
                "request_id",
                None,
            )

            logger.info(
                "request_complete "
                "request_id=%s method=%s "
                "path=%s status_code=%s "
                "latency_ms=%s",
                request_id,
                request.method,
                request.url.path,
                (
                    response.status_code
                    if response
                    else 500
                ),
                latency_ms,
            )