from bson import ObjectId
from fastapi import HTTPException

from app.database.mongodb import users_collection


def user_profile(user):

    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"],
        "full_name": user["full_name"],
        "phone": user["phone"],
        "department": user["department"],
        "role": user["role"],
        "is_active": user["is_active"]
    }


async def get_my_profile(email):

    user = await users_collection.find_one({
        "email": email
    })

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user_profile(user)


async def update_my_profile(email, data):

    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No fields to update"
        )

    result = await users_collection.update_one(
        {"email": email},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user = await users_collection.find_one({
        "email": email
    })

    return user_profile(user)


async def get_all_users(
    role=None,
    department=None,
    is_active=None
):

    query = {}

    if role:
        query["role"] = role

    if department:
        query["department"] = department

    if is_active is not None:
        query["is_active"] = is_active

    users = []

    cursor = users_collection.find(query)

    async for user in cursor:
        users.append(user_profile(user))

    return users


async def get_user_by_id(user_id):

    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user = await users_collection.find_one({
        "_id": ObjectId(user_id)
    })

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user_profile(user)


async def update_user_role(user_id, role):

    if role not in ["user", "admin"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid role"
        )

    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    result = await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"role": role}}
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user = await users_collection.find_one({
        "_id": ObjectId(user_id)
    })

    return user_profile(user)


async def update_user_status(user_id, is_active):

    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    result = await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"is_active": is_active}}
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user = await users_collection.find_one({
        "_id": ObjectId(user_id)
    })

    return user_profile(user)


async def delete_user(user_id):

    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    result = await users_collection.delete_one({
        "_id": ObjectId(user_id)
    })

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "message": "User deleted successfully"
    }