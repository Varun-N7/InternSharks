import logging

from datetime import datetime, timezone
from datetime import timedelta

from hashlib import sha256

from uuid import uuid4

import bcrypt

from fastapi import HTTPException, status

from pymongo.errors import DuplicateKeyError

from app.auth.jwt_handler import (
    create_access_token,
    create_refresh_token,
    decode_token,
)

from app.config import REFRESH_TOKEN_EXPIRE_DAYS

from app.database.mongodb import (
    refresh_tokens_collection,
    users_collection,
)

from app.models.user import UserCreate


logger = logging.getLogger(__name__)


def hash_password(
    password: str,
) -> str:

    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:

    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def hash_refresh_token(
    token: str,
) -> str:

    return sha256(
        token.encode("utf-8")
    ).hexdigest()


def user_to_response(
    user: dict,
) -> dict:

    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "full_name": user.get("full_name"),
        "role": user["role"],
        "is_active": user["is_active"],
    }


async def register_user(
    user_data: UserCreate,
) -> dict:

    existing_email = await users_collection.find_one(
        {
            "email": user_data.email
        }
    )

    if existing_email:

        logger.warning(
            "User registration failed: duplicate email"
        )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    existing_username = await users_collection.find_one(
        {
            "username": user_data.username
        }
    )

    if existing_username:

        logger.warning(
            "User registration failed: duplicate username"
        )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered",
        )

    now = datetime.now(timezone.utc)

    user = {
        "id": str(uuid4()),
        "username": user_data.username,
        "email": str(user_data.email).lower(),
        "password_hash": hash_password(
            user_data.password
        ),
        "full_name": user_data.full_name,
        "role": "user",
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    }

    try:

        await users_collection.insert_one(
            user
        )

    except DuplicateKeyError:

        logger.warning(
            "User registration failed: duplicate email or username"
        )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or username already registered",
        )

    logger.info(
        "User registration successful: %s",
        user["id"],
    )

    return user_to_response(user)


async def login_user(
    email: str,
    password: str,
) -> dict:

    user = await users_collection.find_one(
        {
            "email": email.lower()
        }
    )

    if not user:

        logger.warning(
            "Login failed: invalid credentials"
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not verify_password(
        password,
        user["password_hash"],
    ):

        logger.warning(
            "Login failed: invalid credentials"
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.get("is_active", False):

        logger.warning(
            "Login failed: inactive account"
        )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    access_token = create_access_token(
        user_id=user["id"],
        role=user["role"],
    )

    session_id = str(uuid4())

    refresh_token = create_refresh_token(
        user_id=user["id"],
        role=user["role"],
        session_id=session_id,
    )

    expires_at = datetime.now(
        timezone.utc
    )

    expires_at += timedelta(
        days=REFRESH_TOKEN_EXPIRE_DAYS
    )

    refresh_session = {
        "session_id": session_id,
        "user_id": user["id"],
        "token_hash": hash_refresh_token(
            refresh_token
        ),
        "expires_at": expires_at,
        "revoked": False,
        "created_at": datetime.now(
            timezone.utc
        ),
    }

    await refresh_tokens_collection.insert_one(
        refresh_session
    )

    logger.info(
        "User login successful: %s",
        user["id"],
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user_to_response(user),
    }


async def refresh_access_token(
    refresh_token: str,
) -> dict:

    try:

        payload = decode_token(
            refresh_token
        )

    except ValueError:

        logger.warning(
            "Refresh token authentication failed"
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    if payload.get("type") != "refresh":

        logger.warning(
            "Refresh token authentication failed"
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required",
        )

    session_id = payload.get(
        "session_id"
    )

    user_id = payload.get(
        "sub"
    )

    if not session_id or not user_id:

        logger.warning(
            "Refresh token authentication failed"
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token payload",
        )

    token_hash = hash_refresh_token(
        refresh_token
    )

    session = await refresh_tokens_collection.find_one(
        {
            "session_id": session_id,
            "token_hash": token_hash,
        }
    )

    if not session:

        logger.warning(
            "Refresh token authentication failed"
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh session not found",
        )

    if session.get("revoked", False):

        logger.warning(
            "Refresh token authentication failed"
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked",
        )

    user = await users_collection.find_one(
        {
            "id": user_id
        }
    )

    if not user:

        logger.warning(
            "Refresh token authentication failed"
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.get("is_active", False):

        logger.warning(
            "Refresh token authentication failed"
        )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    new_access_token = create_access_token(
        user_id=user["id"],
        role=user["role"],
    )

    logger.info(
        "Access token refreshed successfully: %s",
        user["id"],
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
    }


async def logout_user(
    refresh_token: str,
) -> None:

    token_hash = hash_refresh_token(
        refresh_token
    )

    result = await refresh_tokens_collection.update_one(
        {
            "token_hash": token_hash,
            "revoked": False,
        },
        {
            "$set": {
                "revoked": True,
                "revoked_at": datetime.now(
                    timezone.utc
                ),
            }
        },
    )

    if result.matched_count == 0:

        logger.warning(
            "Logout failed: invalid or already revoked refresh token"
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or already revoked refresh token",
        )

    logger.info(
        "User logout successful"
    )