from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.auth.dependencies import get_current_admin
from app.models.task import (
    TaskAssignment,
    TaskFilter,
    TaskListResponse,
    TaskResponse,
)
from app.models.user import (
    UserResponse,
)
from app.services.task_service import (
    assign_task,
    get_all_tasks,
)
from app.services.user_service import (
    list_users,
    update_user_role,
    update_user_status,
)


router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


@router.get(
    "/users",
)
async def get_users(
    page: int = Query(
        default=1,
        ge=1,
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
    ),
    current_admin: dict = Depends(
        get_current_admin
    ),
):
    users, total = await list_users(
        page,
        limit,
    )

    return {
        "success": True,
        "page": page,
        "limit": limit,
        "total": total,
        "data": users,
    }


@router.get(
    "/tasks",
    response_model=TaskListResponse,
)
async def get_all_admin_tasks(
    filters: Annotated[
        TaskFilter,
        Query(),
    ],
    current_admin: dict = Depends(
        get_current_admin
    ),
):
    tasks, total = await get_all_tasks(
        filters
    )

    return {
        "success": True,
        "page": filters.page,
        "limit": filters.limit,
        "total": total,
        "data": tasks,
    }


@router.patch(
    "/tasks/{task_id}/assign",
    response_model=TaskResponse,
)
async def assign_admin_task(
    task_id: str,
    assignment: TaskAssignment,
    current_admin: dict = Depends(
        get_current_admin
    ),
):
    return await assign_task(
        task_id,
        assignment.user_id,
    )