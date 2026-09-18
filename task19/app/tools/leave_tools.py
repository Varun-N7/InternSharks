from datetime import date

from app.models.leave import ApplyLeaveArguments
from app.storage.employee_store import get_employee_by_id
from app.storage.leave_store import (
    create_leave_request,
    get_leave_requests_by_employee,
)


def apply_leave(
    employee_id: int,
    leave_type: str,
    start_date: date,
    end_date: date,
    reason: str,
):
    employee = get_employee_by_id(employee_id)

    if not employee:
        raise ValueError("Employee not found")

    arguments = ApplyLeaveArguments(
        employee_id=employee_id,
        leave_type=leave_type,
        start_date=start_date,
        end_date=end_date,
        reason=reason,
    )

    if arguments.end_date < arguments.start_date:
        raise ValueError("End date cannot be before start date")

    if not arguments.reason.strip():
        raise ValueError("Reason is required")

    requested_days = (
        arguments.end_date - arguments.start_date
    ).days + 1

    if arguments.leave_type == "casual":
        available_days = employee.casual_leave
    else:
        available_days = employee.sick_leave

    if requested_days > available_days:
        raise ValueError("Insufficient leave balance")

    request = create_leave_request(
        employee_id=arguments.employee_id,
        leave_type=arguments.leave_type,
        start_date=arguments.start_date,
        end_date=arguments.end_date,
        reason=arguments.reason,
    )

    return request.model_dump(mode="json")


def get_leave_requests(employee_id: int):
    employee = get_employee_by_id(employee_id)

    if not employee:
        raise ValueError("Employee not found")

    requests = get_leave_requests_by_employee(employee_id)

    return [
        request.model_dump(mode="json")
        for request in requests
    ]