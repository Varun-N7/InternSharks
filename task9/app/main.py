from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database.mongodb import (
    client,
    create_indexes,
)
from app.routes.admin import router as admin_router
from app.routes.auth import router as auth_router
from app.routes.user import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await client.admin.command("ping")
    await create_indexes()

    yield

    client.close()


app = FastAPI(
    title="Task 9 - Refresh Tokens & JWT Token Lifecycle",
    version="1.0.0",
    lifespan=lifespan,
)


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(admin_router)


@app.get("/")
async def root():
    return {
        "message": "API is running"
    }