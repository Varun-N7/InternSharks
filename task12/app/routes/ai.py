from fastapi import APIRouter
from fastapi import HTTPException

from groq import APIConnectionError
from groq import APIStatusError
from groq import RateLimitError

from app.models.ai import AIGenerateRequest
from app.services.ai_service import generate_ai_response


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


@router.post("/generate")
async def generate(request: AIGenerateRequest):

    if not request.prompt.strip():

        raise HTTPException(
            status_code=422,
            detail="Prompt cannot be empty",
        )

    try:

        response = await generate_ai_response(
            request.prompt
        )

        return {
            "success": True,
            "status_code": 200,
            "response": response,
        }

    except RateLimitError:

        raise HTTPException(
            status_code=429,
            detail="AI service rate limit exceeded",
        )

    except APIConnectionError:

        raise HTTPException(
            status_code=503,
            detail="AI service is currently unavailable",
        )

    except APIStatusError:

        raise HTTPException(
            status_code=503,
            detail="AI service is currently unavailable",
        )

    except Exception:

        raise HTTPException(
            status_code=503,
            detail="AI service is currently unavailable",
        )