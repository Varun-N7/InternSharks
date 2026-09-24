from fastapi import FastAPI

from app.routes.vision import router as vision_router


app = FastAPI(
    title="Task 25 - Multimodal AI",
    version="1.0.0",
)


app.include_router(
    vision_router
)