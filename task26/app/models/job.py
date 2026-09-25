from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Job(BaseModel):
    job_id: str
    job_type: str
    status: JobStatus = JobStatus.QUEUED

    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None

    input_data: dict = Field(default_factory=dict)
    result: dict | None = None
    error: str | None = None

    worker_id: str | None = None