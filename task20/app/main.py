from fastapi import FastAPI

from app.routes.agent import router


app = FastAPI(
    title="Task 20 - Goal Based AI Agent",
    description="Project Setup Agent with Planning and Tool Execution",
    version="1.0.0",
)


app.include_router(router)


@app.get("/")
def root():
    return {
        "message": "API is running"
    }