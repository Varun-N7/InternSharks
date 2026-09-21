from app.services.project_service import (
    create_project_task,
    get_project_tasks,
    get_task,
    update_task_status,
    delete_project_task,
)


def create_project_task_tool(
    project_id: int,
    title: str,
    priority: str,
    assigned_to=None,
):
    task = create_project_task(
        project_id=project_id,
        title=title,
        priority=priority,
        assigned_to=assigned_to,
    )

    return task.model_dump()


def get_project_tasks_tool(project_id: int):
    tasks = get_project_tasks(project_id)

    return [
        task.model_dump()
        for task in tasks
    ]


def get_task_tool(task_id: int):
    task = get_task(task_id)

    return task.model_dump()


def update_task_status_tool(
    task_id: int,
    status: str,
):
    task = update_task_status(
        task_id=task_id,
        status=status,
    )

    return task.model_dump()


def delete_project_task_tool(task_id: int):
    return delete_project_task(task_id)