from fastapi import APIRouter, Query

from app.config import settings
from app.observability.metrics import (
    calculate_metrics,
)
from app.storage.trace_repository import (
    get_all_traces,
    get_failed_traces,
    get_slow_traces,
    get_trace,
    list_traces,
)


router = APIRouter(
    prefix="/observability",
    tags=["observability"],
)


@router.get("/traces/{trace_id}")
def trace_detail(
    trace_id: str,
):
    trace = get_trace(trace_id)

    if trace is None:
        return {
            "success": False,
            "status_code": 404,
            "data": None,
        }

    return {
        "success": True,
        "status_code": 200,
        "data": trace,
    }


@router.get("/traces")
def traces(
    page: int = Query(1, ge=1),
    page_size: int = Query(
        20,
        ge=1,
        le=100,
    ),
    status: str | None = None,
    model: str | None = None,
    prompt_version: str | None = None,
):
    result = list_traces(
        page=page,
        page_size=page_size,
        status=status,
        model=model,
        prompt_version=prompt_version,
    )

    return {
        "success": True,
        "status_code": 200,
        "data": result,
    }


@router.get("/traces/failures")
def failures(
    error_category: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(
        20,
        ge=1,
        le=100,
    ),
):
    result = get_failed_traces(
        error_category=error_category,
        page=page,
        page_size=page_size,
    )

    return {
        "success": True,
        "status_code": 200,
        "data": result,
    }


@router.get("/traces/slow")
def slow(
    threshold_ms: float | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(
        20,
        ge=1,
        le=100,
    ),
):
    threshold = (
        threshold_ms
        if threshold_ms is not None
        else settings.slow_request_threshold_ms
    )

    result = get_slow_traces(
        threshold_ms=threshold,
        page=page,
        page_size=page_size,
    )

    return {
        "success": True,
        "status_code": 200,
        "data": {
            "threshold_ms": threshold,
            **result,
        },
    }


@router.get("/metrics")
def metrics():
    traces = get_all_traces()

    return {
        "success": True,
        "status_code": 200,
        "data": calculate_metrics(
            traces
        ),
    }