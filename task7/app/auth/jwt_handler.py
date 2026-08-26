from datetime import datetime,timedelta,timezone

from jose import jwt

from app.config import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    JWT_EXPIRE_MINUTES
)

def create_access_token(data: dict):
    to_encode=data.copy()
    expire=datetime.now(timezone.utc)+timedelta(minutes=JWT_EXPIRE_MINUTES)
    to_encode.update({
        "exp":expire
    })

    encoded_jwt=jwt.encode(to_encode,JWT_SECRET_KEY,algorithm=JWT_ALGORITHM)

    return encoded_jwt

def decode_access_token(token: str):
    payload=jwt.decode(token,JWT_SECRET_KEY,algorithms=[JWT_ALGORITHM])
    return payload