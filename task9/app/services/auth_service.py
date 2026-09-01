import hashlib
from datetime import datetime, timedelta, timezone

from passlib.context import CryptContext

from app.config import REFRESH_TOKEN_EXPIRE_DAYS
from app.database.mongodb import refresh_tokens_collection


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(
    password: str,
    password_hash: str,
) -> bool:
    return pwd_context.verify(
        password,
        password_hash,
    )


def hash_refresh_token(
    refresh_token: str,
) -> str:
    return hashlib.sha256(
        refresh_token.encode("utf-8")
    ).hexdigest()


async def create_refresh_session(
    user_id: str,
    session_id: str,
    refresh_token: str,
):
    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(
            days=REFRESH_TOKEN_EXPIRE_DAYS
        )
    )

    token_hash = hash_refresh_token(
        refresh_token
    )

    await refresh_tokens_collection.insert_one(
        {
            "session_id": session_id,
            "user_id": user_id,
            "token_hash": token_hash,
            "expires_at": expires_at,
            "revoked": False,
        }
    )


async def get_refresh_session(
    session_id: str,
    refresh_token: str,
):
    token_hash = hash_refresh_token(
        refresh_token
    )

    return await refresh_tokens_collection.find_one(
        {
            "session_id": session_id,
            "token_hash": token_hash,
        }
    )


async def revoke_refresh_session(
    session_id: str,
):
    await refresh_tokens_collection.update_one(
        {
            "session_id": session_id,
        },
        {
            "$set": {
                "revoked": True,
            }
        },
    )


async def revoke_all_user_sessions(
    user_id: str,
):
    await refresh_tokens_collection.update_many(
        {
            "user_id": user_id,
            "revoked": False,
        },
        {
            "$set": {
                "revoked": True,
            }
        },
    )


def refresh_session_is_expired(
    session: dict,
) -> bool:
    expires_at = session.get("expires_at")

    if not expires_at:
        return True

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(
            tzinfo=timezone.utc
        )

    return expires_at <= datetime.now(
        timezone.utc
    )