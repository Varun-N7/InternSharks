from app.services.employee_service import find_employee


def find_employee_tool(employee_id=None, name=None):
    if employee_id is None and name is None:
        raise ValueError(
            "Employee ID or employee name is required"
        )

    employee = find_employee(
        employee_id=employee_id,
        name=name,
    )

    if not employee:
        raise ValueError("Employee not found")

    return employee