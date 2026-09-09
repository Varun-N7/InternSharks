from typing import Literal

from pydantic import BaseModel, Field


class SummarizeRequest(BaseModel):
    text: str = Field(..., min_length=1)
    summary_type: Literal["brief", "detailed", "bullet_points"]


class SummarizeData(BaseModel):
    summary_type: str
    summary: str
    main_topic: str
    keywords: list[str]


class SummarizeResponse(BaseModel):
    success: bool
    status_code: int
    data: SummarizeData
