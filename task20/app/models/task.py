from typing import Literal

from pydantic import BaseModel, Field


class ProjectTask(BaseModel):
    task_id: int
    project_id: int
    title: str = Field(..., min_length=1)
    priority: Literal["low", "medium", "high"]
    status: Literal["todo", "in_progress", "completed"] = "todo"
    assigned_to: int | None = None