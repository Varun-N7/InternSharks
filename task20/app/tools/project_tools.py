from app.services.employee_service import find_employee
from app.services.project_service import (
    add_project_member,
    create_project,
    get_project,
)


def create_project_tool(
    name: str,
    description: str = "",
):
    project = create_project(
        name=name,
        description=description,
    )

    return project.model_dump()


def get_project_tool(project_id: int):
    project = get_project(project_id)

    return project.model_dump()


def add_project_member_tool(
    project_id: int,
    employee_id: int,
):
    employee = find_employee(
        employee_id=employee_id
    )

    if not employee:
        raise ValueError("Employee not found")

    project = add_project_member(
        project_id=project_id,
        employee_id=employee_id,
    )

    return {
        "project_id": project.project_id,
        "employee_id": employee_id,
        "message": f"{employee['name']} added to project",
        "members": project.members,
    }