from pydantic import BaseModel, Field
from typing import Literal


class Project(BaseModel):
    project_id: int
    name: str = Field(..., min_length=1)
    description: str = ""
    members: list[int] = Field(default_factory=list)
    status: Literal["active", "completed"] = "active"


class ProjectTask(BaseModel):
    task_id: int
    project_id: int
    title: str
    priority: Literal["low", "medium", "high"]
    status: Literal["todo", "in_progress", "completed"] = "todo"
    assigned_to: int | None = None