"""Job model and asyncio worker pool (Celery/Temporal-style queue processing)."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Job:
    """Unit of work placed on the queue."""

    job_id: str
    payload: str


async def worker(
    queue: asyncio.Queue[Job | None],
    process: Callable[[Job], Awaitable[None]],
) -> None:
    """Drain ``queue`` until ``None`` sentinel; call ``process`` per job."""
    while True:
        job = await queue.get()
        try:
            if job is None:
                return
            await process(job)
        finally:
            queue.task_done()


async def run_pool(
    worker_count: int,
    jobs: Sequence[Job],
    process: Callable[[Job], Awaitable[None]],
) -> None:
    """Enqueue ``jobs``, process with ``worker_count`` workers, then stop workers."""
    if worker_count < 1:
        raise ValueError("worker_count must be at least 1")
    q: asyncio.Queue[Job | None] = asyncio.Queue()
    for j in jobs:
        await q.put(j)

    tasks = [asyncio.create_task(worker(q, process)) for _ in range(worker_count)]
    await q.join()
    for _ in range(worker_count):
        await q.put(None)
    await q.join()
    await asyncio.gather(*tasks)
