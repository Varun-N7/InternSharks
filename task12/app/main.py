from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routes.ai import router as ai_router


app = FastAPI(
    title="AI Text Assistant API",
    description="Simple AI Text Assistant using FastAPI and Groq",
    version="1.0.0",
)


app.include_router(ai_router)


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

    error = "VALIDATION_ERROR"

    if exc.status_code == 429:
        error = "AI_RATE_LIMITED"

    elif exc.status_code == 503:
        error = "AI_SERVICE_UNAVAILABLE"

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