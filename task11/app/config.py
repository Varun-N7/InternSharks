import os

from dotenv import load_dotenv


load_dotenv()


MONGO_URI = os.getenv(
    "MONGO_URI"
)

DATABASE_NAME = os.getenv(
    "DATABASE_NAME"
)

JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY"
)

JWT_ALGORITHM = os.getenv(
    "JWT_ALGORITHM"
)

ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv(
    "ACCESS_TOKEN_EXPIRE_MINUTES"
)

REFRESH_TOKEN_EXPIRE_DAYS = os.getenv(
    "REFRESH_TOKEN_EXPIRE_DAYS"
)

APP_ENV = os.getenv(
    "APP_ENV"
)


if not MONGO_URI:

    raise ValueError(
        "MONGO_URI is not configured"
    )


if not DATABASE_NAME:

    raise ValueError(
        "DATABASE_NAME is not configured"
    )


if not JWT_SECRET_KEY:

    raise ValueError(
        "JWT_SECRET_KEY is not configured"
    )


if len(JWT_SECRET_KEY) < 32:

    raise ValueError(
        "JWT_SECRET_KEY must be at least 32 characters"
    )


if not JWT_ALGORITHM:

    raise ValueError(
        "JWT_ALGORITHM is not configured"
    )


if not ACCESS_TOKEN_EXPIRE_MINUTES:

    raise ValueError(
        "ACCESS_TOKEN_EXPIRE_MINUTES is not configured"
    )


if not REFRESH_TOKEN_EXPIRE_DAYS:

    raise ValueError(
        "REFRESH_TOKEN_EXPIRE_DAYS is not configured"
    )


if not APP_ENV:

    raise ValueError(
        "APP_ENV is not configured"
    )


try:

    ACCESS_TOKEN_EXPIRE_MINUTES = int(
        ACCESS_TOKEN_EXPIRE_MINUTES
    )

except ValueError:

    raise ValueError(
        "ACCESS_TOKEN_EXPIRE_MINUTES must be a number"
    )


try:

    REFRESH_TOKEN_EXPIRE_DAYS = int(
        REFRESH_TOKEN_EXPIRE_DAYS
    )

except ValueError:

    raise ValueError(
        "REFRESH_TOKEN_EXPIRE_DAYS must be a number"
    )


if ACCESS_TOKEN_EXPIRE_MINUTES <= 0:

    raise ValueError(
        "ACCESS_TOKEN_EXPIRE_MINUTES must be greater than 0"
    )


if REFRESH_TOKEN_EXPIRE_DAYS <= 0:

    raise ValueError(
        "REFRESH_TOKEN_EXPIRE_DAYS must be greater than 0"
    )