from app.models.leave import LeaveRequest


leave_requests = []
_next_leave_request_id = 1


def create_leave_request(
    employee_id: int,
    leave_type: str,
    start_date,
    end_date,
    reason: str,
):
    global _next_leave_request_id

    request = LeaveRequest(
        leave_request_id=_next_leave_request_id,
        employee_id=employee_id,
        leave_type=leave_type,
        start_date=start_date,
        end_date=end_date,
        reason=reason,
        status="pending",
    )

    leave_requests.append(request)
    _next_leave_request_id += 1

    return request


def get_leave_requests_by_employee(employee_id: int):
    return [
        request
        for request in leave_requests
        if request.employee_id == employee_id
    ]