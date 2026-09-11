from fastapi import APIRouter
from fastapi import HTTPException

from app.models.summarizer import (
    SummarizeData,
    SummarizeRequest,
)
from app.services.summarizer_service import summarize_text


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


@router.post("/summarize")
async def summarize(request: SummarizeRequest):

    try:
        result = summarize_text(
            request.text,
            request.summary_type,
        )

        validated_result = SummarizeData(**result)

        return {
            "success": True,
            "status_code": 200,
            "data": validated_result.model_dump(),
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        )

    except Exception:
        raise HTTPException(
            status_code=502,
            detail="AI summarization failed",
        )