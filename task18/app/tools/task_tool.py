tasks = {
    1: {
        "title": "Buy groceries",
        "status": "pending"
    },
    2: {
        "title": "Finish internship work",
        "status": "completed"
    },
    3: {
        "title": "Call mom",
        "status": "pending"
    }
}


def get_task(task_id: int):
    task = tasks.get(task_id)

    if not task:
        raise ValueError("Task not found")

    return task
