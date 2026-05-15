"""FastAPI BackgroundTasks (catalog: background / async task — v2 narrative)."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from fastapi import APIRouter, BackgroundTasks

logger = logging.getLogger("catalog_showcase.background")

router = APIRouter(prefix="/jobs", tags=["background"])

# In-process record of completed demo jobs (tests can observe side effects)
_completed: list[str] = []


async def _demo_async_work(job_id: str) -> None:
    await asyncio.sleep(0.02)
    _completed.append(job_id)
    logger.info("background_job_done", extra={"job_id": job_id})


@router.post("", status_code=202)
def schedule_demo_job(background_tasks: BackgroundTasks) -> dict[str, Any]:
    """Accepts work and defers async side-effect via BackgroundTasks."""
    import uuid

    job_id = str(uuid.uuid4())
    background_tasks.add_task(_demo_async_work, job_id)
    return {"job_id": job_id, "status": "accepted"}


def reset_completed_for_tests() -> None:
    _completed.clear()


def completed_job_ids() -> list[str]:
    return list(_completed)
