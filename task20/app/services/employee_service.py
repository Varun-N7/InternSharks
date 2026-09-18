EMPLOYEES = [
    {
        "employee_id": 101,
        "name": "Arun",
        "designation": "Backend Developer",
    },
    {
        "employee_id": 102,
        "name": "Priya",
        "designation": "UI/UX Designer",
    },
    {
        "employee_id": 103,
        "name": "Rahul",
        "designation": "QA Engineer",
    },
]


def find_employee(employee_id=None, name=None):
    for employee in EMPLOYEES:
        if employee_id is not None:
            if employee["employee_id"] == employee_id:
                return employee

        if name is not None:
            if employee["name"].lower() == name.lower():
                return employee

    return None