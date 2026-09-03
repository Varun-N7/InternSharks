from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.database.mongodb import (
    client,
    create_indexes,
)
from app.exceptions import (
    general_exception_handler,
    validation_exception_handler,
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


@asynccontextmanager
async def lifespan(
    app: FastAPI,
):
    await client.admin.command("ping")
    await create_indexes()

    yield

    client.close()


app = FastAPI(
    title="Task Management API",
    description="Production-style Task Management Backend",
    version="1.0.0",
    lifespan=lifespan,
)


app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
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
    return {
        "success": True,
        "message": "API and database are available",
    }