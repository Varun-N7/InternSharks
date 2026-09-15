from fastapi import APIRouter, HTTPException

from app.models.chat import (
    ChatHistoryResponse,
    ChatMessage,
    ChatRequest,
    ChatResponse,
)
from app.services.ai_service import (
    AIServiceError,
    InvalidAPIKeyError,
    RateLimitError,
)
from app.services.chat_service import (
    chat_with_ai,
    clear_chat_history,
    get_chat_history,
)


router = APIRouter(
    prefix="/ai",
    tags=["AI Chat"],
)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):

    if not request.session_id.strip():
        raise HTTPException(
            status_code=422,
            detail="Session ID cannot be empty",
        )

    if not request.message.strip():
        raise HTTPException(
            status_code=422,
            detail="Message cannot be empty",
        )

    try:
        response = chat_with_ai(
            request.session_id,
            request.message,
        )

        return {
            "success": True,
            "status_code": 200,
            "data": {
                "session_id": request.session_id,
                "response": response,
            },
        }

    except InvalidAPIKeyError as exc:
        raise HTTPException(
            status_code=401,
            detail=str(exc),
        )

    except RateLimitError as exc:
        raise HTTPException(
            status_code=429,
            detail=str(exc),
        )

    except AIServiceError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        )

    except Exception:
        raise HTTPException(
            status_code=502,
            detail="AI chat failed",
        )


@router.get(
    "/chat/{session_id}/history",
    response_model=ChatHistoryResponse,
)
async def chat_history(session_id: str):

    if not session_id.strip():
        raise HTTPException(
            status_code=422,
            detail="Session ID cannot be empty",
        )

    try:
        history = get_chat_history(session_id)

        messages = [
            ChatMessage(**message)
            for message in history
        ]

        return {
            "success": True,
            "status_code": 200,
            "data": {
                "session_id": session_id,
                "messages": messages,
            },
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.delete("/chat/{session_id}")
async def delete_chat(session_id: str):

    if not session_id.strip():
        raise HTTPException(
            status_code=422,
            detail="Session ID cannot be empty",
        )

    try:
        clear_chat_history(session_id)

        return {
            "success": True,
            "status_code": 200,
            "message": "Conversation history cleared",
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )