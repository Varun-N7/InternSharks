from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.agent.runner import run_agent
from app.models.agent import AgentRequest
from app.storage.run_store import get_run
from app.config import MAX_AGENT_STEPS

router = APIRouter()


@router.post("/agent/run")
def run_agent_endpoint(request: AgentRequest):
    try:
        if not request.goal.strip():
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "status_code": 400,
                    "data": {
                        "error": "Goal cannot be empty"
                    }
                }
            )

        result = run_agent(request.goal)

        # Step-limit failure
        if (
            result.get("status") == "failed"
            and result.get("steps_executed") == MAX_AGENT_STEPS
        ):
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "status_code": 40001,
                    "error": {
                        "code": 40001,
                        "message": f"Agent exceeded maximum steps ({MAX_AGENT_STEPS})",
                        "details": {
                            "max_steps": MAX_AGENT_STEPS,
                            "steps_executed": result.get("steps_executed"),
                            "tools_used": result.get("tools_used", [])
                        }
                    }
                }
            )

        # Success path remains unchanged
        return {
            "success": True,
            "status_code": 200,
            "data": result
        }

    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "status_code": 400,
                "data": {
                    "error": str(e)
                }
            }
        )

    except Exception:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "status_code": 500,
                "data": {
                    "error": "Agent execution failed"
                }
            }
        )


@router.get("/agent/runs/{run_id}")
def get_agent_run(run_id: str):
    run = get_run(run_id)

    if not run:
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "status_code": 404,
                "data": {
                    "error": "Agent run not found"
                }
            }
        )

    return {
        "success": True,
        "status_code": 200,
        "data": run
    }