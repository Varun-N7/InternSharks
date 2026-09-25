import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.queue.fake_redis import FakeRedisQueue
from app.repositories.job_repository import JobRepository
from app.routes.jobs import router as jobs_router
from app.services.ai_service import AIService
from app.workers.worker import JobWorker


job_repository = JobRepository()

job_queue = FakeRedisQueue()

ai_service = AIService()

worker_tasks: list[asyncio.Task] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    global worker_tasks

    worker_tasks = []

    for index in range(settings.worker_count):
        worker = JobWorker(
            repository=job_repository,
            ai_service=ai_service,
        )

        task = asyncio.create_task(
            worker.run()
        )

        worker_tasks.append(task)

    yield

    for task in worker_tasks:
        task.cancel()

    await asyncio.gather(
        *worker_tasks,
        return_exceptions=True,
    )


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(jobs_router)