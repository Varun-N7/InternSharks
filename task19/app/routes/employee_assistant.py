from fastapi import APIRouter, HTTPException

from app.models.assistant import EmployeeAssistantRequest
from app.services.assistant_service import run_assistant
from app.storage.chat_memory import clear_history, get_history


router = APIRouter()


@router.post("/ai/employee-assistant")
def employee_assistant(request: EmployeeAssistantRequest):
    try:
        result = run_assistant(
            request.session_id,
            request.message,
        )

        return {
            "success": True,
            "status_code": 200,
            "data": {
                "response": result["response"],
                "tools_used": result["tools_used"],
            },
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "status_code": 400,
                "data": {
                    "error": str(e),
                },
            },
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "status_code": 500,
                "data": {
                    "error": "Employee assistant service failed",
                },
            },
        )


@router.get("/ai/employee-assistant/{session_id}/history")
def get_session_history(session_id: str):
    history = get_history(session_id)

    return {
        "success": True,
        "status_code": 200,
        "data": {
            "session_id": session_id,
            "history": history,
        },
    }


@router.delete("/ai/employee-assistant/{session_id}")
def delete_session_history(session_id: str):
    clear_history(session_id)

    return {
        "success": True,
        "status_code": 200,
        "data": {
            "message": "Conversation history cleared",
            "session_id": session_id,
        },
    }