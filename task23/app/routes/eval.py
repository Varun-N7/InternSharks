import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.evals.runner import run_evaluation
from app.storage.evaluation_repository import (
    get_evaluation_run,
    get_failed_cases,
    save_evaluation_run,
)


router = APIRouter(prefix="/eval", tags=["evaluation"])


class EvaluationRunRequest(BaseModel):
    suite: str = Field(min_length=1)
    prompt_version: str = "v1"


def demo_answer_provider(case: dict) -> str:
    answers = {
        "eval_001": "Arun manages Project Nova.",
        "eval_002": "The database information is not provided.",
        "eval_003": "Project Nova uses FastAPI.",
        "eval_004": "Priya manages Project Orion.",
        "eval_005": "Project Orion uses Django.",
        "eval_006": "The database information is not available.",
        "eval_007": "Ravi manages Project Atlas.",
        "eval_008": "Project Atlas uses Python.",
        "eval_009": "Arun manages Project Nova.",
        "eval_010": "Project Nova has three backend services.",
        "eval_011": "The salary information is not provided.",
        "eval_012": "Arun works in the Development department.",
        "eval_013": "No. Project Orion uses Django.",
        "eval_014": "Project Orion is managed by Priya.",
        "eval_015": (
            "Project Orion is managed by Priya and uses Django. "
            "The database information is not provided."
        ),
    }

    return answers.get(
        case["id"],
        "The requested information is not provided.",
    )


@router.post("/run")
def run_evaluation_endpoint(request: EvaluationRunRequest):
    if request.suite != "rag_basic":
        raise HTTPException(
            status_code=404,
            detail=f"Evaluation suite not found: {request.suite}",
        )

    if request.prompt_version not in {"v1", "v2"}:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid prompt version: {request.prompt_version}",
        )

    result = run_evaluation(demo_answer_provider)

    run_id = f"eval_run_{uuid.uuid4().hex[:12]}"

    save_evaluation_run(
        run_id=run_id,
        suite=request.suite,
        result=result,
        model="demo-model",
        prompt_version=request.prompt_version,
    )

    return {
        "success": True,
        "status_code": 200,
        "data": {
            "run_id": run_id,
            "suite": request.suite,
            "prompt_version": request.prompt_version,
            "total_cases": result["total_cases"],
            "passed": result["passed"],
            "failed": result["failed"],
            "pass_rate": result["pass_rate"],
        },
    }


@router.get("/runs/{run_id}")
def evaluation_run(run_id: str):
    result = get_evaluation_run(run_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Evaluation run not found: {run_id}",
        )

    return {
        "success": True,
        "data": result,
    }


@router.get("/runs/{run_id}/failures")
def evaluation_failures(run_id: str):
    result = get_evaluation_run(run_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Evaluation run not found: {run_id}",
        )

    return {
        "success": True,
        "data": {
            "run_id": run_id,
            "failures": get_failed_cases(run_id),
        },
    }