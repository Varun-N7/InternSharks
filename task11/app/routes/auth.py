from fastapi import APIRouter, status
from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserCreate, UserResponse
from app.services.auth_service import (
    login_user,
    logout_user,
    refresh_access_token,
    register_user,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=128,
    )


class RefreshRequest(BaseModel):
    refresh_token: str = Field(
        min_length=1,
    )


class LogoutRequest(BaseModel):
    refresh_token: str = Field(
        min_length=1,
    )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_data: UserCreate,
):
    return await register_user(user_data)


@router.post(
    "/login",
)
async def login(
    login_data: LoginRequest,
):
    return await login_user(
        email=str(login_data.email),
        password=login_data.password,
    )


@router.post(
    "/refresh",
)
async def refresh(
    refresh_data: RefreshRequest,
):
    return await refresh_access_token(
        refresh_data.refresh_token
    )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
)
async def logout(
    logout_data: LogoutRequest,
):
    await logout_user(
        logout_data.refresh_token
    )

    return {
        "success": True,
        "message": "Logged out successfully",
    }