import uuid

from app.config import MAX_AGENT_STEPS
from app.agent.state_manager import load_run, save_state
from app.agent.runner import continue_agent


RECOVERABLE_STATUSES = {
    "retrying",
    "partially_completed",
    "failed",
}


def create_recovery_id():
    return "recovery_" + uuid.uuid4().hex[:10]


def can_resume(run):
    if not run:
        return False, "Run not found"

    status = run.get("status")

    if status == "completed":
        return False, "Completed runs cannot be resumed"

    if status == "waiting_for_approval":
        return False, (
            "Run is waiting for human approval. "
            "Approve the pending action first."
        )

    if status == "running":
        return False, "Run is already running"

    if status not in RECOVERABLE_STATUSES:
        return False, (
            f"Run cannot be resumed from status: {status}"
        )

    if run.get("step_count", 0) >= MAX_AGENT_STEPS:
        return False, (
            f"Run already reached maximum steps "
            f"({MAX_AGENT_STEPS})"
        )

    return True, None


def resume_run(run_id):
    run = load_run(run_id)

    allowed, error = can_resume(run)

    if not allowed:
        return {
            "success": False,
            "error": error,
            "run": run,
        }

    run["status"] = "running"

    save_state(run)

    result = continue_agent(run)

    return {
        "success": True,
        "run": result,
    }