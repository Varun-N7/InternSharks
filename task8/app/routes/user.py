from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
from app.models.user import UserUpdate
from app.services import user_service


router = APIRouter()


@router.get("/me")
async def get_me(
    current_user: dict = Depends(get_current_user)
):

    return await user_service.get_my_profile(
        current_user["email"]
    )


@router.put("/me")
async def update_me(
    data: UserUpdate,
    current_user: dict = Depends(get_current_user)
):

    return await user_service.update_my_profile(
        current_user["email"],
        data
    )