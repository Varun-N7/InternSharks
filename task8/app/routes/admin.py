from typing import Optional

from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_admin
from app.models.auth import RoleUpdate, StatusUpdate
from app.services import user_service


router = APIRouter()


@router.get("/admin/users")
async def get_users(
    role: Optional[str] = None,
    department: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_admin: dict = Depends(get_current_admin)
):

    users = await user_service.get_all_users(
        role,
        department,
        is_active
    )

    return {
        "message": "users retrieved successfully",
        "data": users
    }


@router.get("/admin/users/{user_id}")
async def get_user(
    user_id: str,
    current_admin: dict = Depends(get_current_admin)
):

    user = await user_service.get_user_by_id(user_id)

    return {
        "message": "user retrieved successfully",
        "data": user
    }


@router.patch("/admin/users/{user_id}/role")
async def update_role(
    user_id: str,
    data: RoleUpdate,
    current_admin: dict = Depends(get_current_admin)
):

    user = await user_service.update_user_role(
        user_id,
        data.role
    )

    return {
        "message": "user role updated successfully",
        "data": user
    }


@router.patch("/admin/users/{user_id}/status")
async def update_status(
    user_id: str,
    data: StatusUpdate,
    current_admin: dict = Depends(get_current_admin)
):

    user = await user_service.update_user_status(
        user_id,
        data.is_active
    )

    return {
        "message": "user status updated successfully",
        "data": user
    }


@router.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: str,
    current_admin: dict = Depends(get_current_admin)
):

    result = await user_service.delete_user(user_id)

    return result