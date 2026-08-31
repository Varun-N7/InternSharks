from fastapi import HTTPException
from passlib.context import CryptContext

from app.auth.jwt_handler import create_access_token
from app.database.mongodb import users_collection


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


async def register_user(data):

    existing_user = await users_collection.find_one({
        "email": data.email
    })

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )

    hashed_password = pwd_context.hash(data.password)

    user = {
        "username": data.username,
        "email": data.email,
        "password": hashed_password,
        "full_name": data.full_name,
        "phone": data.phone,
        "department": data.department,
        "role": "user",
        "is_active": True
    }

    result = await users_collection.insert_one(user)

    return {
        "id": str(result.inserted_id),
        "username": user["username"],
        "email": user["email"],
        "full_name": user["full_name"],
        "phone": user["phone"],
        "department": user["department"],
        "role": user["role"],
        "is_active": user["is_active"]
    }


async def login_user(data):

    user = await users_collection.find_one({
        "email": data.email
    })

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not user["is_active"]:
        raise HTTPException(
            status_code=403,
            detail="User account is inactive"
        )

    password_correct = pwd_context.verify(
        data.password,
        user["password"]
    )

    if not password_correct:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token({
        "email": user["email"]
    })

    return {
        "message": "login successful",
        "access_token": access_token,
        "username": user["username"],
        "email": user["email"],
        "role": user["role"]
    }