from __future__ import annotations

import asyncio

import pytest

from async_worker_demo.pool import Job, run_pool


@pytest.mark.asyncio
async def test_run_pool_processes_all_jobs() -> None:
    results: list[str] = []

    async def handle(j: Job) -> None:
        results.append(j.payload)

    await run_pool(2, [Job("1", "a"), Job("2", "b"), Job("3", "c")], handle)
    assert sorted(results) == ["a", "b", "c"]


@pytest.mark.asyncio
async def test_worker_stops_on_sentinel() -> None:
    from async_worker_demo.pool import worker

    q: asyncio.Queue[Job | None] = asyncio.Queue()
    seen: list[str] = []

    async def handle(j: Job) -> None:
        seen.append(j.job_id)

    await q.put(Job("x", "p"))
    await q.put(None)
    t = asyncio.create_task(worker(q, handle))
    await q.join()
    await t
    assert seen == ["x"]
