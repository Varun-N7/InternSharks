from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routes.eval import router as eval_router
from app.storage.database import initialize_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="Task 23 - AI Evaluation Framework",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "task23-evaluation",
    }

@app.get("/")
def health():
    return {"service": "API is running",}

app.include_router(eval_router)