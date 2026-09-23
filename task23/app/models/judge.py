from pydantic import BaseModel, ConfigDict, Field


class StructuredAnswer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answer: str
    confidence: float = Field(ge=0.0, le=1.0)