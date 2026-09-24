import time
import uuid
from typing import Any


class Span:
    def __init__(
        self,
        trace_id: str,
        name: str,
    ):
        self.span_id = f"span_{uuid.uuid4().hex[:16]}"
        self.trace_id = trace_id
        self.name = name
        self.status = "running"
        self.attributes: dict[str, Any] = {}
        self._started = time.perf_counter()
        self.duration_ms = 0.0

    def set_attribute(
        self,
        key: str,
        value: Any,
    ) -> None:
        self.attributes[key] = value

    def finish(
        self,
        status: str = "success",
    ) -> float:
        self.duration_ms = round(
            (time.perf_counter() - self._started) * 1000,
            3,
        )
        self.status = status
        return self.duration_ms

    def to_dict(self) -> dict[str, Any]:
        return {
            "span_id": self.span_id,
            "trace_id": self.trace_id,
            "name": self.name,
            "status": self.status,
            "duration_ms": self.duration_ms,
            "attributes": self.attributes,
        }


def create_span(
    trace_id: str,
    name: str,
) -> Span:
    return Span(trace_id, name)