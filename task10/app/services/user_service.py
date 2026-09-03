from fastapi import HTTPException, status
from pymongo.errors import DuplicateKeyError

from app.database.mongodb import users_collection
from app.models.user import UserUpdate


def validate_uuid(
    value: str,
    field_name: str,
) -> str:
    from uuid import UUID

    try:
        UUID(value)
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {field_name}",
        )

    return value


def user_to_response(user: dict) -> dict:
    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "full_name": user.get("full_name"),
        "role": user["role"],
        "is_active": user["is_active"],
    }


async def get_user_by_id(
    user_id: str,
) -> dict:
    validate_uuid(
        user_id,
        "user ID",
    )

    user = await users_collection.find_one(
        {"id": user_id}
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


async def get_current_user_profile(
    current_user: dict,
) -> dict:
    return user_to_response(
        current_user
    )


async def update_current_user_profile(
    current_user: dict,
    user_data: UserUpdate,
) -> dict:
    update_data = user_data.model_dump(
        exclude_unset=True
    )

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )

    if "username" in update_data:
        existing_user = await users_collection.find_one(
            {
                "username": update_data["username"],
                "id": {
                    "$ne": current_user["id"]
                },
            }
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already registered",
            )

    try:
        await users_collection.update_one(
            {"id": current_user["id"]},
            {
                "$set": update_data
            },
        )
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered",
        )

    updated_user = await get_user_by_id(
        current_user["id"]
    )

    return user_to_response(
        updated_user
    )


async def list_users(
    page: int,
    limit: int,
) -> tuple[list[dict], int]:
    skip = (
        page - 1
    ) * limit

    total = await users_collection.count_documents(
        {}
    )

    cursor = (
        users_collection
        .find({})
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )

    users = await cursor.to_list(
        length=limit
    )

    return (
        [
            user_to_response(user)
            for user in users
        ],
        total,
    )


async def update_user_role(
    user_id: str,
    role: str,
    current_admin_id: str,
) -> dict:
    validate_uuid(
        user_id,
        "user ID",
    )

    if role not in {
        "user",
        "admin",
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be either user or admin",
        )

    if (
        user_id == current_admin_id
        and role != "admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot remove your own admin role",
        )

    user = await get_user_by_id(
        user_id
    )

    await users_collection.update_one(
        {"id": user["id"]},
        {
            "$set": {
                "role": role
            }
        },
    )

    updated_user = await get_user_by_id(
        user["id"]
    )

    return user_to_response(
        updated_user
    )


async def update_user_status(
    user_id: str,
    is_active: bool,
    current_admin_id: str,
) -> dict:
    validate_uuid(
        user_id,
        "user ID",
    )

    if (
        user_id == current_admin_id
        and not is_active
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate your own account",
        )

    user = await get_user_by_id(
        user_id
    )

    await users_collection.update_one(
        {"id": user["id"]},
        {
            "$set": {
                "is_active": is_active
            }
        },
    )

    updated_user = await get_user_by_id(
        user["id"]
    )

    return user_to_response(
        updated_user
    )