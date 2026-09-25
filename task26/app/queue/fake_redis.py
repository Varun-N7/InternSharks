from queue import Queue, Empty
from typing import Optional


class FakeRedisQueue:
    """
    In-memory queue used as a lightweight Redis replacement.
    """

    def __init__(self):
        self._queue = Queue()

    async def enqueue(self, job_id: str) -> None:
        """
        Add a job ID to the queue.

        This is async because the jobs route awaits enqueue().
        """
        self._queue.put(job_id)

    def dequeue(self, timeout: Optional[float] = None) -> Optional[str]:
        """
        Remove and return the next job ID.
        """
        try:
            return self._queue.get(timeout=timeout)
        except Empty:
            return None

    def task_done(self) -> None:
        """
        Mark the current queue item as completed.
        """
        self._queue.task_done()

    def join(self) -> None:
        """
        Wait until all queued jobs are completed.
        """
        self._queue.join()

    def size(self) -> int:
        """
        Return number of waiting jobs.
        """
        return self._queue.qsize()

    def empty(self) -> bool:
        """
        Return True if the queue is empty.
        """
        return self._queue.empty()

    def clear(self) -> None:
        """
        Remove all waiting jobs.
        """
        while True:
            try:
                self._queue.get_nowait()
                self._queue.task_done()
            except Empty:
                break