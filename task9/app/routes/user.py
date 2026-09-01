from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import get_current_user
from app.models.user import (
    UserResponse,
    UserUpdate,
)
from app.services.user_service import (
    serialize_user,
    update_user_profile,
)


router = APIRouter(
    tags=["User"],
)


@router.get(
    "/me",
    response_model=UserResponse,
)
async def get_me(
    current_user: dict = Depends(
        get_current_user
    ),
):
    return serialize_user(
        current_user
    )


@router.put(
    "/me",
    response_model=UserResponse,
)
async def update_me(
    data: UserUpdate,
    current_user: dict = Depends(
        get_current_user
    ),
):
    updates = data.model_dump(
        exclude_unset=True
    )

    result = await update_user_profile(
        current_user["_id"],
        updates,
    )

    if result == "USERNAME_EXISTS":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )

    return serialize_user(result)