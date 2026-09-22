from pydantic import BaseModel, Field


class AgentRunRequest(BaseModel):
    goal: str = Field(..., min_length=1)
    openrouter_failure_mode: str | None = None


class ApprovalRequest(BaseModel):
    approved: bool