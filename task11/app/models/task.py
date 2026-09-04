from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


TaskStatus = Literal[
    "todo",
    "in_progress",
    "completed",
]

TaskPriority = Literal[
    "low",
    "medium",
    "high",
]


class TaskCreate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=200,
    )
    description: str | None = Field(
        default=None,
        max_length=2000,
    )
    status: TaskStatus = "todo"
    priority: TaskPriority = "medium"
    assigned_to: str | None = None
    due_date: datetime | None = None


class TaskUpdate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=200,
    )
    description: str | None = Field(
        default=None,
        max_length=2000,
    )
    status: TaskStatus
    priority: TaskPriority
    assigned_to: str | None = None
    due_date: datetime | None = None


class TaskStatusUpdate(BaseModel):
    status: TaskStatus


class TaskAssignment(BaseModel):
    user_id: str


class TaskResponse(BaseModel):
    id: str
    title: str
    description: str | None = None
    status: TaskStatus
    priority: TaskPriority
    created_by: str
    assigned_to: str | None = None
    due_date: datetime | None = None
    created_at: datetime
    updated_at: datetime


class TaskListResponse(BaseModel):
    success: bool
    page: int
    limit: int
    total: int
    data: list[TaskResponse]


class TaskFilter(BaseModel):
    page: int = Field(
        default=1,
        ge=1,
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=100,
    )
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    assigned_to: str | None = None
    search: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )