from app.models.project import Project, ProjectTask


employees = [
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


projects = []
tasks = []

_next_project_id = 1
_next_task_id = 1


def find_employee(employee_id=None, name=None):
    for employee in employees:
        if employee_id is not None:
            if employee["employee_id"] == employee_id:
                return employee

        if name is not None:
            if employee["name"].lower() == name.lower():
                return employee

    raise ValueError("Employee not found")


from app.reliability.errors import RetryableError

project_temporary_failure_attempts = {}


def create_project(name, description=""):
    global _next_project_id

    name = name.strip()

    if not name:
        raise ValueError("Project name is required")

    if "retry" in name.lower() or "temp" in name.lower():
        attempts = project_temporary_failure_attempts.get(name.lower(), 0) + 1
        project_temporary_failure_attempts[name.lower()] = attempts

        if attempts == 1:
            raise RetryableError("Temporary service failure")

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


def get_project(project_id):
    for project in projects:
        if project.project_id == project_id:
            return project

    raise ValueError("Project not found")


def list_projects():
    return projects


def add_project_member(project_id, employee_id):
    project = get_project(project_id)

    find_employee(employee_id=employee_id)

    if employee_id in project.members:
        raise ValueError("Employee is already a project member")

    project.members.append(employee_id)

    return project


def create_project_task(
    project_id,
    title,
    priority,
    assigned_to=None,
):
    global _next_task_id

    project = get_project(project_id)

    if not title or not title.strip():
        raise ValueError("Task title is required")

    if priority not in ["low", "medium", "high"]:
        raise ValueError("Invalid priority")

    if assigned_to is not None:
        find_employee(employee_id=assigned_to)

        if assigned_to not in project.members:
            raise ValueError(
                "Assigned employee must be a project member"
            )

    task = ProjectTask(
        task_id=_next_task_id,
        project_id=project_id,
        title=title.strip(),
        priority=priority,
        assigned_to=assigned_to,
    )

    tasks.append(task)
    _next_task_id += 1

    return task


def get_project_tasks(project_id):
    get_project(project_id)

    return [
        task
        for task in tasks
        if task.project_id == project_id
    ]


def get_task(task_id):
    for task in tasks:
        if task.task_id == task_id:
            return task

    raise ValueError("Task not found")


def update_task_status(task_id, status):
    if status not in [
        "todo",
        "in_progress",
        "completed",
    ]:
        raise ValueError("Invalid task status")

    task = get_task(task_id)

    task.status = status

    return task


def delete_project_task(task_id):
    task = get_task(task_id)

    tasks.remove(task)

    return {
        "task_id": task_id,
        "message": "Task deleted successfully",
    }