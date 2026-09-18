from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    goal: str = Field(..., min_length=1)