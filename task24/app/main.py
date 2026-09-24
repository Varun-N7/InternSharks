from fastapi import FastAPI

from app.middleware.logging import (
    RequestLoggingMiddleware,
)
from app.middleware.request_tracking import (
    RequestTrackingMiddleware,
)
from app.routes.ai import router as ai_router
from app.routes.observability import (
    router as observability_router,
)
from app.storage.database import (
    initialize_database,
)


initialize_database()

app = FastAPI(
    title="Task 24 - AI Observability",
    version="1.0.0",
)

app.add_middleware(
    RequestTrackingMiddleware
)

app.add_middleware(
    RequestLoggingMiddleware
)

app.include_router(ai_router)
app.include_router(
    observability_router
)


@app.get("/")
def root():
    return {
        "success": True,
        "status_code": 200,
        "data": {
            "service": "AI Observability",
            "task": 24,
        },
    }


@app.get("/health")
def health():
    return {
        "success": True,
        "status_code": 200,
        "data": {
            "status": "healthy",
        },
    }