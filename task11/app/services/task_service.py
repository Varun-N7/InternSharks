import logging

from datetime import datetime, timezone

from uuid import UUID, uuid4

from fastapi import HTTPException, status

from pymongo.errors import DuplicateKeyError

from app.database.mongodb import (
    tasks_collection,
    users_collection,
)

from app.models.task import (
    TaskCreate,
    TaskFilter,
    TaskUpdate,
)


logger = logging.getLogger(__name__)


def validate_uuid(
    value: str,
    field_name: str,
) -> str:

    try:

        UUID(value)

    except (ValueError, AttributeError):

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {field_name}",
        )

    return value


def task_to_response(
    task: dict,
) -> dict:

    return {
        "id": task["id"],
        "title": task["title"],
        "description": task.get("description"),
        "status": task["status"],
        "priority": task["priority"],
        "created_by": task["created_by"],
        "assigned_to": task.get("assigned_to"),
        "due_date": task.get("due_date"),
        "created_at": task["created_at"],
        "updated_at": task["updated_at"],
    }


async def get_task_by_id(
    task_id: str,
) -> dict:

    validate_uuid(
        task_id,
        "task ID",
    )

    task = await tasks_collection.find_one(
        {
            "id": task_id
        }
    )

    if not task:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task


def user_can_access_task(
    task: dict,
    user_id: str,
) -> bool:

    return (
        task.get("created_by") == user_id
        or task.get("assigned_to") == user_id
    )


async def create_task(
    task_data: TaskCreate,
    current_user: dict,
) -> dict:

    assigned_to = task_data.assigned_to

    if assigned_to:

        validate_uuid(
            assigned_to,
            "assigned user ID",
        )

        assigned_user = await users_collection.find_one(
            {
                "id": assigned_to
            }
        )

        if not assigned_user:

            logger.warning(
                "Task creation failed: assigned user not found"
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assigned user not found",
            )

    now = datetime.now(timezone.utc)

    task = {
        "id": str(uuid4()),
        "title": task_data.title,
        "description": task_data.description,
        "status": task_data.status,
        "priority": task_data.priority,
        "created_by": current_user["id"],
        "assigned_to": assigned_to,
        "due_date": task_data.due_date,
        "created_at": now,
        "updated_at": now,
    }

    try:

        await tasks_collection.insert_one(
            task
        )

    except Exception:

        logger.error(
            "Task creation failed for user: %s",
            current_user["id"],
            exc_info=True,
        )

        raise

    logger.info(
        "Task created successfully: %s by user: %s",
        task["id"],
        current_user["id"],
    )

    return task_to_response(task)


async def get_user_tasks(
    current_user: dict,
    filters: TaskFilter,
) -> tuple[list[dict], int]:

    user_id = current_user["id"]

    ownership_query = {
        "$or": [
            {
                "created_by": user_id
            },
            {
                "assigned_to": user_id
            },
        ]
    }

    query: dict = {
        "$and": [
            ownership_query,
        ]
    }

    if filters.status:

        query["$and"].append(
            {
                "status": filters.status
            }
        )

    if filters.priority:

        query["$and"].append(
            {
                "priority": filters.priority
            }
        )

    if filters.assigned_to:

        validate_uuid(
            filters.assigned_to,
            "assigned user ID",
        )

        query["$and"].append(
            {
                "assigned_to": filters.assigned_to
            }
        )

    if filters.search:

        query["$and"].append(
            {
                "title": {
                    "$regex": filters.search,
                    "$options": "i",
                }
            }
        )

    skip = (
        filters.page - 1
    ) * filters.limit

    total = await tasks_collection.count_documents(
        query
    )

    cursor = (
        tasks_collection
        .find(query)
        .sort("created_at", -1)
        .skip(skip)
        .limit(filters.limit)
    )

    tasks = await cursor.to_list(
        length=filters.limit
    )

    return (
        [
            task_to_response(task)
            for task in tasks
        ],
        total,
    )


async def get_task_for_user(
    task_id: str,
    current_user: dict,
) -> dict:

    task = await get_task_by_id(
        task_id
    )

    if current_user.get("role") == "admin":

        return task_to_response(task)

    if not user_can_access_task(
        task,
        current_user["id"],
    ):

        logger.warning(
            "Task access denied for user: %s",
            current_user["id"],
        )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this task",
        )

    return task_to_response(task)


async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    current_user: dict,
) -> dict:

    task = await get_task_by_id(
        task_id
    )

    is_admin = (
        current_user.get("role")
        == "admin"
    )

    is_owner = (
        task.get("created_by")
        == current_user["id"]
    )

    is_assigned = (
        task.get("assigned_to")
        == current_user["id"]
    )

    if (
        not is_admin
        and not is_owner
        and not is_assigned
    ):

        logger.warning(
            "Task update denied for user: %s",
            current_user["id"],
        )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this task",
        )

    update_data = task_data.model_dump(
        exclude_unset=True
    )

    assigned_to = update_data.get(
        "assigned_to"
    )

    if assigned_to:

        try:

            validate_uuid(
                assigned_to,
                "assigned user ID",
            )

        except HTTPException:

            logger.warning(
                "Task update failed: invalid assigned user ID"
            )

            raise

        assigned_user = await users_collection.find_one(
            {
                "id": assigned_to
            }
        )

        if not assigned_user:

            logger.warning(
                "Task update failed: assigned user not found"
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assigned user not found",
            )

    try:

        await tasks_collection.update_one(
            {
                "id": task_id
            },
            {
                "$set": {
                    **update_data,
                    "updated_at": datetime.now(
                        timezone.utc
                    ),
                }
            },
        )

    except Exception:

        logger.error(
            "Task update failed: %s",
            task_id,
            exc_info=True,
        )

        raise

    updated_task = await get_task_by_id(
        task_id
    )

    logger.info(
        "Task updated successfully: %s by user: %s",
        task_id,
        current_user["id"],
    )

    return task_to_response(
        updated_task
    )


async def update_task_status(
    task_id: str,
    new_status: str,
    current_user: dict,
) -> dict:

    task = await get_task_by_id(
        task_id
    )

    is_admin = (
        current_user.get("role")
        == "admin"
    )

    is_owner = (
        task.get("created_by")
        == current_user["id"]
    )

    is_assigned = (
        task.get("assigned_to")
        == current_user["id"]
    )

    if (
        not is_admin
        and not is_owner
        and not is_assigned
    ):

        logger.warning(
            "Task status update denied for user: %s",
            current_user["id"],
        )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this task",
        )

    try:

        await tasks_collection.update_one(
            {
                "id": task_id
            },
            {
                "$set": {
                    "status": new_status,
                    "updated_at": datetime.now(
                        timezone.utc
                    ),
                }
            },
        )

    except Exception:

        logger.error(
            "Task status update failed: %s",
            task_id,
            exc_info=True,
        )

        raise

    updated_task = await get_task_by_id(
        task_id
    )

    logger.info(
        "Task status updated successfully: %s by user: %s",
        task_id,
        current_user["id"],
    )

    return task_to_response(
        updated_task
    )


async def delete_task(
    task_id: str,
    current_user: dict,
) -> None:

    task = await get_task_by_id(
        task_id
    )

    is_admin = (
        current_user.get("role")
        == "admin"
    )

    is_owner = (
        task.get("created_by")
        == current_user["id"]
    )

    if not is_admin and not is_owner:

        logger.warning(
            "Task deletion denied for user: %s",
            current_user["id"],
        )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only the task owner or an admin "
                "can delete this task"
            ),
        )

    try:

        result = await tasks_collection.delete_one(
            {
                "id": task_id
            }
        )

    except Exception:

        logger.error(
            "Task deletion failed: %s",
            task_id,
            exc_info=True,
        )

        raise

    if result.deleted_count == 0:

        logger.warning(
            "Task deletion failed: task not found: %s",
            task_id,
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    logger.info(
        "Task deleted successfully: %s by user: %s",
        task_id,
        current_user["id"],
    )


async def get_all_tasks(
    filters: TaskFilter,
) -> tuple[list[dict], int]:

    query: dict = {}

    if filters.status:

        query["status"] = filters.status

    if filters.priority:

        query["priority"] = filters.priority

    if filters.assigned_to:

        validate_uuid(
            filters.assigned_to,
            "assigned user ID",
        )

        query["assigned_to"] = (
            filters.assigned_to
        )

    if filters.search:

        query["title"] = {
            "$regex": filters.search,
            "$options": "i",
        }

    skip = (
        filters.page - 1
    ) * filters.limit

    total = await tasks_collection.count_documents(
        query
    )

    cursor = (
        tasks_collection
        .find(query)
        .sort("created_at", -1)
        .skip(skip)
        .limit(filters.limit)
    )

    tasks = await cursor.to_list(
        length=filters.limit
    )

    return (
        [
            task_to_response(task)
            for task in tasks
        ],
        total,
    )


async def assign_task(
    task_id: str,
    user_id: str,
) -> dict:

    validate_uuid(
        task_id,
        "task ID",
    )

    validate_uuid(
        user_id,
        "user ID",
    )

    user = await users_collection.find_one(
        {
            "id": user_id
        }
    )

    if not user:

        logger.warning(
            "Task assignment failed: user not found"
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned user not found",
        )

    await get_task_by_id(
        task_id
    )

    try:

        result = await tasks_collection.update_one(
            {
                "id": task_id
            },
            {
                "$set": {
                    "assigned_to": user_id,
                    "updated_at": datetime.now(
                        timezone.utc
                    ),
                }
            },
        )

    except Exception:

        logger.error(
            "Task assignment failed: %s",
            task_id,
            exc_info=True,
        )

        raise

    if result.matched_count == 0:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    updated_task = await get_task_by_id(
        task_id
    )

    logger.info(
        "Task assigned successfully: %s to user: %s",
        task_id,
        user_id,
    )

    return task_to_response(
        updated_task
    )