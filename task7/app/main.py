from fastapi import FastAPI

from app.routes.user_routes import router


app = FastAPI(
    title="JWT Authentication API"
)

app.include_router(router)