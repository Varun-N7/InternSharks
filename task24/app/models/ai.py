from pydantic import BaseModel, Field


class AIAskRequest(BaseModel):
    message: str = Field(min_length=1)


class AIAskResponse(BaseModel):
    response: str
    trace_id: str