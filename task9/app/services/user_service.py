import uuid

from pymongo.errors import DuplicateKeyError

from app.database.mongodb import users_collection
from app.services.auth_service import hash_password


def serialize_user(user: dict) -> dict:
    return {
        "id": user["_id"],
        "username": user["username"],
        "email": user["email"],
        "full_name": user.get("full_name"),
        "phone": user.get("phone"),
        "department": user.get("department"),
        "role": user.get("role", "user"),
        "is_active": user.get("is_active", True),
    }


async def get_user_by_email(email: str):
    return await users_collection.find_one(
        {"email": email}
    )


async def get_user_by_id(user_id: str):
    return await users_collection.find_one(
        {"_id": user_id}
    )


async def create_user(
    username: str,
    email: str,
    password: str,
    full_name: str | None = None,
    phone: str | None = None,
    department: str | None = None,
):
    user = {
        "_id": str(uuid.uuid4()),
        "username": username,
        "email": email,
        "password_hash": hash_password(password),
        "full_name": full_name,
        "phone": phone,
        "department": department,
        "role": "user",
        "is_active": True,
    }

    try:
        await users_collection.insert_one(user)
    except DuplicateKeyError:
        return None

    return user


async def update_user_profile(
    user_id: str,
    updates: dict,
):
    if "username" in updates:
        existing = await users_collection.find_one(
            {
                "username": updates["username"],
                "_id": {"$ne": user_id},
            }
        )

        if existing:
            return "USERNAME_EXISTS"

    await users_collection.update_one(
        {"_id": user_id},
        {"$set": updates},
    )

    return await get_user_by_id(user_id)


async def list_users(
    role: str | None = None,
    department: str | None = None,
    is_active: bool | None = None,
):
    query = {}

    if role is not None:
        query["role"] = role

    if department is not None:
        query["department"] = department

    if is_active is not None:
        query["is_active"] = is_active

    cursor = users_collection.find(query)

    return await cursor.to_list(length=None)


async def update_user_role(
    user_id: str,
    role: str,
):
    result = await users_collection.update_one(
        {"_id": user_id},
        {"$set": {"role": role}},
    )

    return result.matched_count > 0


async def update_user_status(
    user_id: str,
    is_active: bool,
):
    result = await users_collection.update_one(
        {"_id": user_id},
        {"$set": {"is_active": is_active}},
    )

    return result.matched_count > 0


async def delete_user(user_id: str):
    result = await users_collection.delete_one(
        {"_id": user_id}
    )

    return result.deleted_count > 0