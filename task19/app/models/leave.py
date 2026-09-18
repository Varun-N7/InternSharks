from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class ApplyLeaveArguments(BaseModel):
    employee_id: int
    leave_type: Literal["casual", "sick"]
    start_date: date
    end_date: date
    reason: str = Field(..., min_length=1)


class LeaveRequest(BaseModel):
    leave_request_id: int
    employee_id: int
    leave_type: Literal["casual", "sick"]
    start_date: date
    end_date: date
    reason: str
    status: str