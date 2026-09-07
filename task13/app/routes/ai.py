from fastapi import APIRouter
from fastapi import HTTPException

from app.models.ai import AIAnalyzeRequest
from app.services.ai_service import analyze_text


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


@router.post("/analyze")
async def analyze(request: AIAnalyzeRequest):

    try:

        result = await analyze_text(request.text)

        return {
            "success": True,
            "status_code": 200,
            "data": result,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=f"AI analysis failed: {str(exc)}",
        )
