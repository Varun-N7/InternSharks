from app.storage.run_repository import (
    save_run,
    get_run,
)


def create_run(run_id, goal):
    run = {
        "run_id": run_id,
        "goal": goal,
        "status": "running",
        "step_count": 0,
        "messages": [],
        "pending_action": None,
        "execution_trace": [],
    }

    save_run(run)

    return run


def load_run(run_id):
    return get_run(run_id)


def save_state(run):
    save_run(run)