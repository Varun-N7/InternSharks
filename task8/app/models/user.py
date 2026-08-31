from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserRequest(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=100)
    full_name: str = Field(min_length=1, max_length=100)
    phone: str = Field(min_length=1, max_length=20)
    department: str = Field(min_length=1, max_length=50)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50
    )

    full_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100
    )

    phone: Optional[str] = Field(
        None,
        min_length=1,
        max_length=20
    )

    department: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50
    )


class UserResponse(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    phone: str
    department: str
    role: str
    is_active: bool