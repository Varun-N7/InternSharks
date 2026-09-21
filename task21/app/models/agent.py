from pydantic import BaseModel, Field


class AgentRunRequest(BaseModel):
    goal: str = Field(..., min_length=1)


class ApprovalRequest(BaseModel):
    approved: bool