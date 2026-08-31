from fastapi import APIRouter, status

from app.models.user import UserRequest, UserLogin
from app.services import auth_service


router = APIRouter()


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED
)
async def register_user(data: UserRequest):

    user = await auth_service.register_user(data)

    return {
        "message": "user created successfully",
        "data": user
    }


@router.post("/login")
async def login_user(data: UserLogin):

    user = await auth_service.login_user(data)

    return user