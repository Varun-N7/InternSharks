from fastapi import FastAPI

from app.routes.employee_assistant import router


app = FastAPI(
    title="AI Employee Assistant",
    description="AI Employee Assistant with Multi-Tool Calling",
    version="1.0.0",
)

app.include_router(router)


@app.get("/")
def root():
    return {
        "message": "API is running"
    }