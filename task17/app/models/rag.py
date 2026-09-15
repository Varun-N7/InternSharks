from pydantic import BaseModel, Field


class RAGUploadData(BaseModel):
    document_id: str
    file_name: str
    chunks_created: int


class RAGUploadResponse(BaseModel):
    success: bool
    status_code: int
    data: RAGUploadData


class RAGAskRequest(BaseModel):
    document_id: str = Field(..., min_length=1)
    question: str = Field(..., min_length=1)
    top_k: int = Field(default=3, ge=1, le=10)


class RAGAskData(BaseModel):
    document_id: str
    question: str
    answer: str


class RAGAskResponse(BaseModel):
    success: bool
    status_code: int
    data: RAGAskData


class RAGDocumentData(BaseModel):
    document_id: str
    file_name: str
    chunks_created: int


class RAGDocumentResponse(BaseModel):
    success: bool
    status_code: int
    data: RAGDocumentData