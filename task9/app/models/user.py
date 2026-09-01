from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50,
    )
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=128,
    )
    full_name: str | None = Field(
        default=None,
        max_length=100,
    )
    phone: str | None = Field(
        default=None,
        max_length=30,
    )
    department: str | None = Field(
        default=None,
        max_length=100,
    )


class UserUpdate(BaseModel):
    username: str | None = Field(
        default=None,
        min_length=3,
        max_length=50,
    )
    full_name: str | None = Field(
        default=None,
        max_length=100,
    )
    phone: str | None = Field(
        default=None,
        max_length=30,
    )
    department: str | None = Field(
        default=None,
        max_length=100,
    )


class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    full_name: str | None = None
    phone: str | None = None
    department: str | None = None
    role: str
    is_active: bool


class RoleUpdate(BaseModel):
    role: Literal["user", "admin"]


class StatusUpdate(BaseModel):
    is_active: bool