from fastapi import FastAPI

from app.routes.user_route import router


app = FastAPI(title="User Authentication API")


app.include_router(router)