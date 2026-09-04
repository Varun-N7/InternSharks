from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.auth.dependencies import get_current_user
from app.models.task import (
    TaskCreate,
    TaskFilter,
    TaskListResponse,
    TaskResponse,
    TaskStatusUpdate,
    TaskUpdate,
)
from app.services.task_service import (
    create_task,
    delete_task,
    get_task_for_user,
    get_user_tasks,
    update_task,
    update_task_status,
)


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
)


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_new_task(
    task_data: TaskCreate,
    current_user: dict = Depends(get_current_user),
):
    return await create_task(
        task_data,
        current_user,
    )


@router.get(
    "",
    response_model=TaskListResponse,
)
async def get_tasks(
    filters: Annotated[
        TaskFilter,
        Query(),
    ],
    current_user: dict = Depends(get_current_user),
):
    tasks, total = await get_user_tasks(
        current_user,
        filters,
    )

    return {
        "success": True,
        "page": filters.page,
        "limit": filters.limit,
        "total": total,
        "data": tasks,
    }


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
)
async def get_single_task(
    task_id: str,
    current_user: dict = Depends(get_current_user),
):
    return await get_task_for_user(
        task_id,
        current_user,
    )


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
)
async def update_existing_task(
    task_id: str,
    task_data: TaskUpdate,
    current_user: dict = Depends(get_current_user),
):
    return await update_task(
        task_id,
        task_data,
        current_user,
    )


@router.patch(
    "/{task_id}/status",
    response_model=TaskResponse,
)
async def change_task_status(
    task_id: str,
    status_data: TaskStatusUpdate,
    current_user: dict = Depends(get_current_user),
):
    return await update_task_status(
        task_id,
        status_data.status,
        current_user,
    )


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_task(
    task_id: str,
    current_user: dict = Depends(get_current_user),
):
    await delete_task(
        task_id,
        current_user,
    )