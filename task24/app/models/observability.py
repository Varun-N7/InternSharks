from typing import Any

from pydantic import BaseModel


class MetricsResponse(BaseModel):
    total_requests: int
    successful_requests: int
    failed_requests: int
    timeout_requests: int
    average_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    total_tokens: int
    total_cost_usd: float
    by_model: dict[str, Any]


class FailureResponse(BaseModel):
    trace_id: str
    status: str
    error_category: str | None
    error_message: str | None
    model: str | None
    prompt_version: str | None