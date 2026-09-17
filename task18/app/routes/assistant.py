from fastapi import APIRouter, HTTPException

from app.models.assistant import AssistantRequest
from app.services.assistant_service import run_assistant

router = APIRouter()


@router.post("/ai/assistant")
def assistant(request: AssistantRequest):
    try:
        return run_assistant(request.message)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Assistant service failed"
        )