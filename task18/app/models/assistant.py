from typing import Literal

from pydantic import BaseModel, Field


class AssistantRequest(BaseModel):
    message: str = Field(..., min_length=1)


class CalculatorArguments(BaseModel):
    operation: Literal["add", "subtract", "multiply", "divide"]
    a: float
    b: float


class GetTaskArguments(BaseModel):
    task_id: int