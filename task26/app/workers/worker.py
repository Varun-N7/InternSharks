import asyncio
from datetime import datetime, timezone

from app.models.job import JobStatus
from app.queue.fake_redis import FakeRedisQueue
from app.repositories.job_repository import JobRepository
from app.services.ai_service import AIService


class JobWorker:
    def __init__(
        self,
        repository: JobRepository,
        ai_service: AIService,
        queue: FakeRedisQueue | None = None,
        worker_id: str = "worker-1",
    ) -> None:
        self.repository = repository
        self.ai_service = ai_service
        self.queue = queue
        self.worker_id = worker_id

    async def run(self) -> None:
        if self.queue is None:
            return

        while True:
            job_id = await self.queue.pop()

            try:
                await self.process_job(job_id)
            finally:
                self.queue.task_done()

    async def process_job(
        self,
        job_id: str,
    ) -> None:
        job = self.repository.get(job_id)

        if job is None:
            return

        if job.status == JobStatus.CANCELLED:
            return

        job.status = JobStatus.PROCESSING
        job.started_at = datetime.now(
            timezone.utc
        )
        job.worker_id = self.worker_id

        self.repository.update(job)

        try:
            result = await self._run_ai(job)

            job.status = JobStatus.COMPLETED
            job.result = result
            job.completed_at = datetime.now(
                timezone.utc
            )

        except Exception as exc:
            job.status = JobStatus.FAILED
            job.error = str(exc)
            job.completed_at = datetime.now(
                timezone.utc
            )

        self.repository.update(job)

    async def _run_ai(self, job):
        document_text = job.input_data.get(
            "document_text",
            "",
        )

        simulate_failure = job.input_data.get(
            "simulate_failure",
            False,
        )

        if hasattr(
            self.ai_service,
            "analyze_document",
        ):
            return await self.ai_service.analyze_document(
                document_text,
                simulate_failure=simulate_failure,
            )

        if hasattr(
            self.ai_service,
            "process",
        ):
            result = self.ai_service.process(job)

            if asyncio.iscoroutine(result):
                result = await result

            return result

        raise RuntimeError(
            "AIService has no supported processing method"
        )