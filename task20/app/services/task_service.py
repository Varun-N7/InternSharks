from app.models.task import ProjectTask
from app.services.project_service import get_project

tasks: list[ProjectTask] = []

_next_task_id = 1


def create_project_task(
    project_id: int,
    title: str,
    priority: str,
    assigned_to: int | None = None
):
    global _next_task_id

    project = get_project(project_id)

    if not title or not title.strip():
        raise ValueError("Task title is required")

    if priority not in ["low", "medium", "high"]:
        raise ValueError("Invalid priority")

    if assigned_to is not None:
        if assigned_to not in project.members:
            raise ValueError("Assigned employee must be a project member")

    task = ProjectTask(
        task_id=_next_task_id,
        project_id=project_id,
        title=title.strip(),
        priority=priority,
        assigned_to=assigned_to
    )

    tasks.append(task)
    _next_task_id += 1

    return task


def list_project_tasks(project_id: int):
    get_project(project_id)

    return [
        task
        for task in tasks
        if task.project_id == project_id
    ]


def update_task_status(task_id: int, status: str):
    if status not in ["todo", "in_progress", "completed"]:
        raise ValueError("Invalid task status")

    for task in tasks:
        if task.task_id == task_id:
            task.status = status
            return task

    raise ValueError("Task not found")
    