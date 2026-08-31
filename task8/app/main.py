from fastapi import FastAPI

from app.routes.auth import router as auth_router
from app.routes.user import router as user_router
from app.routes.admin import router as admin_router


app = FastAPI(
    title="RBAC User Management API"
)


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(admin_router)


@app.get("/")
def home():

    return {
        "message": "API is running"
    }