from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth.dependencies import require_admin
from app.models.user import (
    RoleUpdate,
    StatusUpdate,
    UserResponse,
)
from app.services.auth_service import (
    revoke_all_user_sessions,
)
from app.services.user_service import (
    delete_user,
    get_user_by_id,
    list_users,
    serialize_user,
    update_user_role,
    update_user_status,
)


router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


@router.get(
    "/users",
    response_model=list[UserResponse],
)
async def get_all_users(
    role: str | None = Query(
        default=None,
        pattern="^(user|admin)$",
    ),
    department: str | None = None,
    is_active: bool | None = None,
    current_admin: dict = Depends(
        require_admin
    ),
):
    users = await list_users(
        role=role,
        department=department,
        is_active=is_active,
    )

    return [
        serialize_user(user)
        for user in users
    ]


@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
)
async def get_specific_user(
    user_id: str,
    current_admin: dict = Depends(
        require_admin
    ),
):
    user = await get_user_by_id(
        user_id
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return serialize_user(user)


@router.patch(
    "/users/{user_id}/role",
    response_model=UserResponse,
)
async def change_user_role(
    user_id: str,
    data: RoleUpdate,
    current_admin: dict = Depends(
        require_admin
    ),
):
    if user_id == current_admin["_id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot change your own role",
        )

    user = await get_user_by_id(
        user_id
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    await update_user_role(
        user_id,
        data.role,
    )

    updated_user = await get_user_by_id(
        user_id
    )

    return serialize_user(
        updated_user
    )


@router.patch(
    "/users/{user_id}/status",
    response_model=UserResponse,
)
async def change_user_status(
    user_id: str,
    data: StatusUpdate,
    current_admin: dict = Depends(
        require_admin
    ),
):
    if user_id == current_admin["_id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot change your own account status",
        )

    user = await get_user_by_id(
        user_id
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    await update_user_status(
        user_id,
        data.is_active,
    )

    if not data.is_active:
        await revoke_all_user_sessions(
            user_id
        )

    updated_user = await get_user_by_id(
        user_id
    )

    return serialize_user(
        updated_user
    )


@router.delete(
    "/users/{user_id}"
)
async def remove_user(
    user_id: str,
    current_admin: dict = Depends(
        require_admin
    ),
):
    user = await get_user_by_id(
        user_id
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    await revoke_all_user_sessions(
        user_id
    )

    await delete_user(
        user_id
    )

    return {
        "message": "User deleted successfully"
    }