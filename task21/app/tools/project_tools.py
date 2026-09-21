from app.services.project_service import (
    create_project,
    get_project,
    list_projects,
    add_project_member,
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


def list_projects_tool():
    return [
        project.model_dump()
        for project in list_projects()
    ]


def add_project_member_tool(
    project_id: int,
    employee_id: int,
):
    project = add_project_member(
        project_id=project_id,
        employee_id=employee_id,
    )

    return {
        "project_id": project.project_id,
        "employee_id": employee_id,
        "members": project.members,
    }