from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.models.agent import (
    AgentRunRequest,
    ApprovalRequest,
)

from app.agent.runner import (
    start_agent,
    approve_and_resume,
)

from app.agent.state_manager import (
    load_run,
)

from app.services.approval_service import (
    get_approval_action,
    mark_approved,
    mark_rejected,
)


router = APIRouter()


@router.post("/agent/runs")
def create_agent_run(request: AgentRunRequest):

    if not request.goal.strip():
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "status_code": 400,
                "error": {
                    "code": 400,
                    "message": "Goal cannot be empty",
                },
            },
        )

    try:
        result = start_agent(
            request.goal.strip()
        )

        return {
            "success": True,
            "status_code": 200,
            "data": result,
        }

    except ValueError as error:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "status_code": 400,
                "error": {
                    "code": 400,
                    "message": str(error),
                },
            },
        )

    except Exception:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "status_code": 500,
                "error": {
                    "code": 500,
                    "message": "Agent execution failed",
                },
            },
        )


@router.get("/agent/runs/{run_id}")
def get_agent_run(run_id: str):

    run = load_run(run_id)

    if not run:
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "status_code": 404,
                "error": {
                    "code": 404,
                    "message": "Run not found",
                },
            },
        )

    return {
        "success": True,
        "status_code": 200,
        "data": {
            "run_id": run["run_id"],
            "goal": run["goal"],
            "status": run["status"],
            "step_count": run["step_count"],
            "pending_action": run["pending_action"],
            "execution_trace": run[
                "execution_trace"
            ],
        },
    }


@router.post(
    "/agent/runs/{run_id}/actions/{action_id}/approval"
)
def approve_agent_action(
    run_id: str,
    action_id: str,
    request: ApprovalRequest,
):

    run = load_run(run_id)

    if not run:
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "status_code": 404,
                "error": {
                    "code": 404,
                    "message": "Run not found",
                },
            },
        )

    action = get_approval_action(action_id)

    if not action:
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "status_code": 404,
                "error": {
                    "code": 404,
                    "message": "Action not found",
                },
            },
        )

    if action["run_id"] != run_id:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "status_code": 400,
                "error": {
                    "code": 400,
                    "message": "Action does not belong to this run",
                },
            },
        )

    if action["status"] != "pending":
        return JSONResponse(
            status_code=409,
            content={
                "success": False,
                "status_code": 409,
                "error": {
                    "code": 409,
                    "message": (
                        "Action has already been "
                        + action["status"]
                    ),
                },
            },
        )

    if run["status"] != "waiting_for_approval":
        return JSONResponse(
            status_code=409,
            content={
                "success": False,
                "status_code": 409,
                "error": {
                    "code": 409,
                    "message": "Run is not waiting for approval",
                },
            },
        )

    if not request.approved:

        mark_rejected(action_id)

        run["pending_action"]["status"] = (
            "rejected"
        )

        run["status"] = "rejected"

        run["execution_trace"].append(
            {
                "step": run["step_count"] + 1,
                "type": "approval",
                "tool": action["tool"],
                "status": "rejected",
                "action_id": action_id,
            }
        )

        from app.agent.state_manager import save_state

        save_state(run)

        return {
            "success": True,
            "status_code": 200,
            "data": {
                "run_id": run_id,
                "status": "rejected",
                "action_id": action_id,
                "message": (
                    "Action rejected. "
                    "The write operation was not executed."
                ),
            },
        }

    try:
        mark_approved(action_id)

        result = approve_and_resume(
            run,
            action,
        )

        return {
            "success": True,
            "status_code": 200,
            "data": result,
        }

    except ValueError as error:

        run["status"] = "failed"

        from app.agent.state_manager import save_state

        save_state(run)

        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "status_code": 400,
                "error": {
                    "code": 400,
                    "message": str(error),
                },
            },
        )

    except Exception:

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "status_code": 500,
                "error": {
                    "code": 500,
                    "message": "Approved action execution failed",
                },
            },
        )