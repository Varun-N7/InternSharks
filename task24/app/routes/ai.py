from fastapi import APIRouter, HTTPException, Request

from app.models.ai import AIAskRequest
from app.observability.logging import log_ai_event
from app.observability.tracing import Trace
from app.services.ai_service import AIService
from app.services.errors import AIServiceError
from app.storage.trace_repository import save_trace


router = APIRouter(
    prefix="/ai",
    tags=["ai"],
)


@router.post("/ask")
def ask(
    payload: AIAskRequest,
    request: Request,
):
    trace = Trace(
        request_type="ai_ask"
    )

    try:
        service = AIService()

        answer = service.ask(
            payload.message,
            trace,
        )

        trace.finish(
            status="success"
        )

        trace_data = trace.to_dict()

        save_trace(trace_data)

        log_ai_event(
            "ai_request_complete",
            trace_id=trace.trace_id,
            model=trace.model,
            prompt_version=trace.prompt_version,
            status=trace.status,
            latency_ms=trace.total_duration_ms,
        )

        return {
            "success": True,
            "status_code": 200,
            "data": {
                "response": answer,
                "trace_id": trace.trace_id,
            },
        }

    except AIServiceError as exc:
        trace.finish(
            status=exc.status,
            error_category=exc.category,
            error_message=str(exc),
        )

        save_trace(
            trace.to_dict()
        )

        log_ai_event(
            "ai_request_failed",
            trace_id=trace.trace_id,
            model=trace.model,
            prompt_version=trace.prompt_version,
            status=trace.status,
            error_category=trace.error_category,
        )

        raise HTTPException(
            status_code=504
            if exc.status == "timeout"
            else 502,
            detail={
                "error": str(exc),
                "trace_id": trace.trace_id,
                "error_category": exc.category,
            },
        )