from datetime import datetime
from threading import Lock
from uuid import uuid4

from app.models.job import Job


class JobRepository:

    def __init__(self):
        self._jobs: dict[str, Job] = {}
        self._lock = Lock()

    def create(
        self,
        job_id: str | None = None,
        job_type: str = "document_analysis",
        analysis_type: str | None = None,
        filename: str | None = None,
        created_at: datetime | None = None,
        **kwargs,
    ) -> Job:

        if job_id is None:
            job_id = str(uuid4())

        job_data = {
            "job_id": job_id,
            "job_type": job_type,
            "created_at": created_at or datetime.now(),
        }

        model_fields = getattr(Job, "model_fields", {})

        if analysis_type is not None and "analysis_type" in model_fields:
            job_data["analysis_type"] = analysis_type

        if filename is not None and "filename" in model_fields:
            job_data["filename"] = filename

        for key, value in kwargs.items():
            if key in model_fields:
                job_data[key] = value

        job = Job(**job_data)

        with self._lock:
            self._jobs[job_id] = job

        return job

    def get(self, job_id: str) -> Job | None:
        with self._lock:
            return self._jobs.get(job_id)

    def update(self, job: Job) -> Job:
        with self._lock:
            self._jobs[job.job_id] = job

        return job

    def update_status(self, job_id: str, status) -> Job | None:
        with self._lock:
            job = self._jobs.get(job_id)

            if job is None:
                return None

            job.status = status
            self._jobs[job_id] = job

            return job

    def delete(self, job_id: str) -> bool:
        with self._lock:
            if job_id not in self._jobs:
                return False

            del self._jobs[job_id]
            return True

    def list_all(self) -> list[Job]:
        with self._lock:
            return list(self._jobs.values())

    def list(
        self,
        status: str | None = None,
        analysis_type: str | None = None,
    ) -> list[Job]:

        with self._lock:
            jobs = list(self._jobs.values())

        if status is not None:
            filtered_jobs = []

            for job in jobs:
                job_status = (
                    job.status.value
                    if hasattr(job.status, "value")
                    else job.status
                )

                if job_status == status:
                    filtered_jobs.append(job)

            jobs = filtered_jobs

        if analysis_type is not None:
            jobs = [
                job
                for job in jobs
                if getattr(job, "analysis_type", None)
                == analysis_type
            ]

        return jobs

    def count(self) -> int:
        with self._lock:
            return len(self._jobs)

    def clear(self) -> None:
        with self._lock:
            self._jobs.clear()