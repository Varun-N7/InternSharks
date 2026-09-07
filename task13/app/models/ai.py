from pydantic import BaseModel, Field


class AIAnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1)


class AIAnalyzeData(BaseModel):
    summary: str
    category: str
    priority: str
    sentiment: str
    keywords: list[str]


class AIAnalyzeResponse(BaseModel):
    success: bool
    status_code: int
    data: AIAnalyzeData
