# background_tasks.py
from __future__ import annotations

import asyncio
import logging
from threading import Lock

logger = logging.getLogger("status_hub.jobs")

_completed_job_ids: list[str] = []
_completed_lock = Lock()


def reset_completed_for_tests() -> None:
    """Clear job state between tests. Not for production use."""
    with _completed_lock:
        _completed_job_ids.clear()


def completed_job_ids() -> list[str]:
    with _completed_lock:
        return list(_completed_job_ids)


async def demo_async_work(job_id: str) -> None:
    """
    Simulates async I/O work. Scheduled via FastAPI BackgroundTasks,
    which runs async tasks in the active event loop.
    """
    await asyncio.sleep(0.02)
    with _completed_lock:
        _completed_job_ids.append(job_id)
    logger.info("background_job_done", extra={"job_id": job_id})