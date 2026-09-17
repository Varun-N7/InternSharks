from fastapi import FastAPI

from app.routes.assistant import router


app = FastAPI(
    title="AI Tool Calling Assistant",
    description="Simple AI assistant using OpenRouter tool calling",
    version="1.0.0"
)


app.include_router(router)


@app.get("/")
def root():
    return {
        "message": "API is running"
    }