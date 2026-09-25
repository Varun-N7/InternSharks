from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.models.job import JobStatus
from app.repositories.job_repository import JobRepository
from app.services.ai_service import AIService
from app.workers.worker import JobWorker
from app.queue.fake_redis import FakeRedisQueue


router = APIRouter(
    prefix="/jobs",
    tags=["jobs"],
)


# Shared application components
job_repository = JobRepository()
job_queue = FakeRedisQueue()
ai_service = AIService()

job_worker = JobWorker(
    job_queue,
    job_repository,
    ai_service,
)


# Supported document analysis types
SUPPORTED_ANALYSIS_TYPES = {
    "summary",
    "extract",
}


@router.get("/health")
async def jobs_health():
    return {
        "success": True,
        "status_code": 200,
        "message": "Jobs router is working",
    }


@router.post("/document-analysis", status_code=202)
async def create_document_analysis_job(
    file: UploadFile = File(...),
    analysis_type: str = Form(default="summary"),
):
    try:
        # Normalize the analysis type
        analysis_type = analysis_type.strip().lower()

        # Validate analysis type BEFORE creating the job
        if analysis_type not in SUPPORTED_ANALYSIS_TYPES:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": (
                        f"Unsupported analysis_type: '{analysis_type}'. "
                        f"Supported types: "
                        f"{', '.join(sorted(SUPPORTED_ANALYSIS_TYPES))}"
                    ),
                    "error_category": "invalid_analysis_type",
                    "supported_analysis_types": sorted(
                        SUPPORTED_ANALYSIS_TYPES
                    ),
                },
            )

        # Read uploaded file
        file_bytes = await file.read()

        # Reject empty files
        if not file_bytes:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "File is empty",
                    "error_category": "empty_file",
                },
            )

        # Create job
        job = job_repository.create(
            job_type="document_analysis",
            analysis_type=analysis_type,
            filename=file.filename or "unknown",
            content_type=file.content_type or "",
            file_bytes=file_bytes,
        )

        # Queue job for background processing
        await job_queue.enqueue(job.job_id)

        return {
            "success": True,
            "status_code": 202,
            "data": {
                "job_id": job.job_id,
                "status": (
                    job.status.value
                    if hasattr(job.status, "value")
                    else job.status
                ),
            },
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(exc),
                "error_category": "job_creation_error",
            },
        ) from exc


@router.get("/{job_id}")
async def get_job(job_id: str):
    job = job_repository.get(job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    return {
        "success": True,
        "status_code": 200,
        "data": job.model_dump(),
    }


@router.get("/{job_id}/result")
async def get_job_result(job_id: str):
    job = job_repository.get(job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    status = (
        job.status.value
        if hasattr(job.status, "value")
        else job.status
    )

    if status != JobStatus.COMPLETED.value:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "Job is not completed",
                "status": status,
            },
        )

    return {
        "success": True,
        "status_code": 200,
        "data": {
            "job_id": job.job_id,
            "status": status,
            "result": job.result,
        },
    }


@router.get("")
async def list_jobs(
    status: str | None = None,
    analysis_type: str | None = None,
):
    jobs = job_repository.list(
        status=status,
        analysis_type=analysis_type,
    )

    return {
        "success": True,
        "status_code": 200,
        "data": {
            "jobs": [
                job.model_dump()
                for job in jobs
            ],
        },
    }


@router.post("/{job_id}/cancel")
async def cancel_job(job_id: str):
    job = job_repository.get(job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    current_status = (
        job.status.value
        if hasattr(job.status, "value")
        else job.status
    )

    if current_status != JobStatus.QUEUED.value:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "Only queued jobs can be cancelled",
                "status": current_status,
            },
        )

    job_repository.update_status(
        job_id,
        JobStatus.CANCELLED,
    )

    return {
        "success": True,
        "status_code": 200,
        "data": {
            "job_id": job_id,
            "status": JobStatus.CANCELLED.value,
        },
    }