from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
from app.models.user import UserResponse, UserUpdate
from app.services.user_service import (
    get_current_user_profile,
    update_current_user_profile,
)


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/me",
    response_model=UserResponse,
)
async def get_me(
    current_user: dict = Depends(get_current_user),
):
    return await get_current_user_profile(
        current_user
    )


@router.put(
    "/me",
    response_model=UserResponse,
)
async def update_me(
    user_data: UserUpdate,
    current_user: dict = Depends(get_current_user),
):
    return await update_current_user_profile(
        current_user,
        user_data,
    )