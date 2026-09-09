from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routes.summarizer import router as summarizer_router


app = FastAPI(
    title="AI Document & Text Summarization API",
    description="AI-powered text summarization using FastAPI and OpenRouter",
    version="1.0.0",
)


app.include_router(summarizer_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "status_code": 422,
            "error": "VALIDATION_ERROR",
            "message": "Invalid request data",
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):

    error = "AI_SERVICE_ERROR"

    if exc.status_code == 422:
        error = "VALIDATION_ERROR"

    elif exc.status_code == 401:
        error = "INVALID_API_KEY"

    elif exc.status_code == 429:
        error = "AI_RATE_LIMITED"

    elif exc.status_code == 502:
        error = "AI_SERVICE_ERROR"

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "status_code": exc.status_code,
            "error": error,
            "message": str(exc.detail),
        },
    )


@app.get("/")
async def root():

    return {
        "success": True,
        "message": "API is running",
    }
