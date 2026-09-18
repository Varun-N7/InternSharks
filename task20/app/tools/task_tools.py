from app.services.employee_service import find_employee
from app.services.task_service import (
    create_project_task,
    list_project_tasks,
    update_task_status,
)


def create_project_task_tool(
    project_id: int,
    title: str,
    priority: str,
    assigned_to=None,
):
    if assigned_to is not None:
        employee = find_employee(
            employee_id=assigned_to
        )

        if not employee:
            raise ValueError("Employee not found")

    task = create_project_task(
        project_id=project_id,
        title=title,
        priority=priority,
        assigned_to=assigned_to,
    )

    return task.model_dump()


def list_project_tasks_tool(project_id: int):
    tasks = list_project_tasks(project_id)

    return [
        task.model_dump()
        for task in tasks
    ]


def update_task_status_tool(
    task_id: int,
    status: str,
):
    task = update_task_status(
        task_id=task_id,
        status=status,
    )

    return task.model_dump()