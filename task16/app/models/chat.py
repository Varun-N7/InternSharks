from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)


class ChatData(BaseModel):
    session_id: str
    response: str


class ChatResponse(BaseModel):
    success: bool
    status_code: int
    data: ChatData


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatHistoryData(BaseModel):
    session_id: str
    messages: list[ChatMessage]


class ChatHistoryResponse(BaseModel):
    success: bool
    status_code: int
    data: ChatHistoryData