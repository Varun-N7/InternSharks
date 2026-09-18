from pydantic import BaseModel, Field


class EmployeeAssistantRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)