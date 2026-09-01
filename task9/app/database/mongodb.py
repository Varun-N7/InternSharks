from motor.motor_asyncio import AsyncIOMotorClient

from app.config import DATABASE_NAME, MONGO_URI


client = AsyncIOMotorClient(
    MONGO_URI,
    tz_aware=True,
)

database = client[DATABASE_NAME]

users_collection = database["users"]

refresh_tokens_collection = database["refresh_tokens"]


async def create_indexes():
    await users_collection.create_index(
        "email",
        unique=True,
        name="unique_email",
    )

    await users_collection.create_index(
        "username",
        unique=True,
        name="unique_username",
    )

    await refresh_tokens_collection.create_index(
        "session_id",
        unique=True,
        name="unique_session_id",
    )

    await refresh_tokens_collection.create_index(
        "token_hash",
        unique=True,
        name="unique_token_hash",
    )

    await refresh_tokens_collection.create_index(
        "expires_at",
        expireAfterSeconds=0,
        name="refresh_session_ttl",
    )