from app.models.employee import Employee


employees = [
    Employee(
        employee_id=101,
        name="Arun",
        department="Development",
        designation="Backend Developer",
        casual_leave=8,
        sick_leave=5,
    ),
    Employee(
        employee_id=102,
        name="Priya",
        department="Design",
        designation="UI/UX Designer",
        casual_leave=6,
        sick_leave=4,
    ),
]


def get_employee_by_id(employee_id: int):
    for employee in employees:
        if employee.employee_id == employee_id:
            return employee

    return None