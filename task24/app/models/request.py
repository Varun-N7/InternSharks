from pydantic import BaseModel, Field


class AIRequest(BaseModel):
    message: str = Field(min_length=1)