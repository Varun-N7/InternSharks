from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.models.agent import AgentRunRequest
from app.agent.runner import start_agent, approve_and_resume
from app.agent.recovery import resume_run
from app.agent.state_manager import load_run


router = APIRouter()


class ApprovalRequest(BaseModel):
    approved: bool


@router.post("/agent/runs")
def create_agent_run(request: AgentRunRequest):
    result = start_agent(request.goal)

    if result.get("success") is False:
        return JSONResponse(
            status_code=400,
            content=result
        )

    return {
        "success": True,
        "status_code": 200,
        "data": result
    }


@router.post("/agent/runs/{run_id}/actions/{action_id}/approval")
def approve_agent_action(
    run_id: str,
    action_id: str,
    request: ApprovalRequest
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
                    "message": "Run not found"
                }
            }
        )

    pending_action = run.get("pending_action")

    if not pending_action:
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "status_code": 404,
                "error": {
                    "code": 404,
                    "message": "No pending action found"
                }
            }
        )

    if pending_action.get("action_id") != action_id:
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "status_code": 404,
                "error": {
                    "code": 404,
                    "message": "Action does not belong to this run"
                }
            }
        )

    if not request.approved:
        pending_action["status"] = "rejected"
        run["pending_action"] = None
        run["status"] = "rejected"

        from app.agent.state_manager import save_state

        save_state(run)

        return {
            "success": True,
            "status_code": 200,
            "data": run
        }

    # IMPORTANT:
    # Current runner.py expects:
    # approve_and_resume(run, action)
    result = approve_and_resume(
        run,
        pending_action
    )

    return {
        "success": True,
        "status_code": 200,
        "data": result
    }


@router.post("/agent/runs/{run_id}/resume")
def resume_agent_run(run_id: str):
    result = resume_run(run_id)

    if result.get("success") is False:
        return JSONResponse(
            status_code=400,
            content=result
        )

    return {
        "success": True,
        "status_code": 200,
        "data": result.get("run")
    }


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
                    "message": "Run not found"
                }
            }
        )

    return {
        "success": True,
        "status_code": 200,
        "data": run
    }