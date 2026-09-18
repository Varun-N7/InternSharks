from typing import Literal

from pydantic import BaseModel, Field


class Project(BaseModel):
    project_id: int
    name: str = Field(..., min_length=1)
    description: str = ""
    members: list[int] = []
    status: Literal["active", "completed"] = "active"