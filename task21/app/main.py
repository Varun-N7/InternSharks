from fastapi import FastAPI

from app.storage.database import init_database
from app.routes.agent import router


init_database()

app = FastAPI(
    title="Task 21 - Stateful AI Agent",
    description=(
        "Stateful AI Agent with Human Approval Workflow"
    ),
    version="1.0.0",
)

app.include_router(router)


@app.get("/")
def root():
    return {
        "message": "API is running"
    }