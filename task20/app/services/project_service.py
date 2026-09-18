from app.models.project import Project
from app.storage.project_store import projects


_next_project_id = 1


def create_project(name: str, description: str = ""):
    global _next_project_id

    name = name.strip()

    if not name:
        raise ValueError("Project name is required")

    for project in projects:
        if project.name.lower() == name.lower():
            raise ValueError("Project with this name already exists")

    project = Project(
        project_id=_next_project_id,
        name=name,
        description=description.strip(),
    )

    projects.append(project)
    _next_project_id += 1

    return project


def get_project(project_id: int):
    if not isinstance(project_id, int):
        raise ValueError("Invalid project ID")

    for project in projects:
        if project.project_id == project_id:
            return project

    raise ValueError("Project not found")


def add_project_member(project_id: int, employee_id: int):
    project = get_project(project_id)

    if employee_id in project.members:
        raise ValueError("Employee is already a project member")

    project.members.append(employee_id)

    return project