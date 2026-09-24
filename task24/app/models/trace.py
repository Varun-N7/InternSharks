from typing import Any

from pydantic import BaseModel


class SpanResponse(BaseModel):
    span_id: str
    trace_id: str
    name: str
    status: str
    duration_ms: float
    attributes: dict[str, Any] = {}


class TraceResponse(BaseModel):
    trace_id: str
    request_type: str
    model: str | None
    prompt_version: str | None
    status: str
    start_time: str
    end_time: str | None
    total_duration_ms: float
    prompt_tokens: int | None
    completion_tokens: int | None
    total_tokens: int | None
    estimated_cost_usd: float | None
    error_category: str | None
    error_message: str | None
    spans: list[SpanResponse]