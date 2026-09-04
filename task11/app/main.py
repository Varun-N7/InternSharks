import logging

from contextlib import asynccontextmanager

from time import perf_counter

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.database.mongodb import (
    client,
    check_database_connection,
    create_indexes,
)

from app.exceptions import (
    general_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)

from app.logging_config import (
    setup_logging,
)

from app.routes.admin import (
    router as admin_router,
)

from app.routes.auth import (
    router as auth_router,
)

from app.routes.tasks import (
    router as tasks_router,
)

from app.routes.users import (
    router as users_router,
)


setup_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info(
        "Application startup"
    )

    database_connected = await check_database_connection()

    if database_connected:

        await create_indexes()

    else:

        logger.error(
            "Application startup database check failed"
        )

    yield

    logger.info(
        "Application shutdown"
    )

    client.close()

    logger.info(
        "MongoDB connection closed"
    )


app = FastAPI(
    title="Task Management API",
    description="Production-style Task Management Backend",
    version="1.0.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def request_logging_middleware(
    request,
    call_next,
):

    start_time = perf_counter()

    try:

        response = await call_next(
            request
        )

        processing_time = (
            perf_counter() - start_time
        ) * 1000

        logger.info(
            "%s %s - %s - %.0fms",
            request.method,
            request.url.path,
            response.status_code,
            processing_time,
        )

        return response

    except Exception:

        processing_time = (
            perf_counter() - start_time
        ) * 1000

        logger.error(
            "%s %s - unexpected error - %.0fms",
            request.method,
            request.url.path,
            processing_time,
        )

        raise


app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)

app.add_exception_handler(
    HTTPException,
    http_exception_handler,
)

app.add_exception_handler(
    Exception,
    general_exception_handler,
)


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(tasks_router)
app.include_router(admin_router)


@app.get(
    "/",
    tags=["Health"],
)
async def root():

    return {
        "success": True,
        "message": "Task Management API is running",
    }


@app.get(
    "/health",
    tags=["Health"],
)
async def health_check():

    database_connected = await check_database_connection()

    if not database_connected:

        return JSONResponse(
            status_code=503,
            content={
                "success": False,
                "status_code": 503,
                "status": "unhealthy",
                "database": "disconnected",
            },
        )

    return {
        "success": True,
        "status_code": 200,
        "status": "healthy",
        "database": "connected",
    }