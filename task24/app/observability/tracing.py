import time
import uuid
from datetime import datetime, timezone
from typing import Any

from app.observability.spans import Span


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Trace:
    def __init__(
        self,
        request_type: str = "ai_request",
    ):
        self.trace_id = f"trace_{uuid.uuid4().hex}"
        self.request_type = request_type
        self.model: str | None = None
        self.prompt_version: str | None = None
        self.status = "running"
        self.start_time = utc_now()
        self.end_time: str | None = None
        self.total_duration_ms = 0.0

        self.prompt_tokens: int | None = None
        self.completion_tokens: int | None = None
        self.total_tokens: int | None = None
        self.estimated_cost_usd: float | None = None

        self.error_category: str | None = None
        self.error_message: str | None = None

        self.spans: list[Span] = []
        self._started = time.perf_counter()

    def start_span(self, name: str) -> Span:
        span = Span(
            trace_id=self.trace_id,
            name=name,
        )
        self.spans.append(span)
        return span

    def finish(
        self,
        status: str = "success",
        error_category: str | None = None,
        error_message: str | None = None,
    ) -> None:
        self.status = status
        self.error_category = error_category
        self.error_message = error_message
        self.total_duration_ms = round(
            (time.perf_counter() - self._started) * 1000,
            3,
        )
        self.end_time = utc_now()

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "request_type": self.request_type,
            "model": self.model,
            "prompt_version": self.prompt_version,
            "status": self.status,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "total_duration_ms": self.total_duration_ms,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "estimated_cost_usd": self.estimated_cost_usd,
            "error_category": self.error_category,
            "error_message": self.error_message,
            "spans": [
                span.to_dict()
                for span in self.spans
            ],
        }