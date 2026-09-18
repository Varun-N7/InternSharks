from app.storage.employee_store import get_employee_by_id


def get_employee(employee_id: int):
    employee = get_employee_by_id(employee_id)

    if not employee:
        raise ValueError("Employee not found")

    return employee.model_dump()


def get_leave_balance(employee_id: int):
    employee = get_employee_by_id(employee_id)

    if not employee:
        raise ValueError("Employee not found")

    return {
        "employee_id": employee.employee_id,
        "casual_leave": employee.casual_leave,
        "sick_leave": employee.sick_leave,
    }