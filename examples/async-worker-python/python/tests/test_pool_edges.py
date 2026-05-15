"""Pool configuration and failure propagation."""

from __future__ import annotations

import asyncio

import pytest

from async_worker_demo.pool import Job, run_pool, worker


async def _noop(_j: Job) -> None:
    return None


@pytest.mark.asyncio
async def test_run_pool_rejects_zero_workers() -> None:
    with pytest.raises(ValueError, match="at least 1"):
        await run_pool(0, [Job("1", "a")], _noop)


@pytest.mark.asyncio
async def test_worker_process_exception_propagates() -> None:
    q: asyncio.Queue[Job | None] = asyncio.Queue()
    await q.put(Job("1", "x"))

    async def boom(_j: Job) -> None:
        raise RuntimeError("task failed")

    t = asyncio.create_task(worker(q, boom))
    with pytest.raises(RuntimeError, match="task failed"):
        await asyncio.wait_for(t, timeout=2.0)
    await q.join()


@pytest.mark.asyncio
async def test_worker_handles_sentinel_after_job() -> None:
    q: asyncio.Queue[Job | None] = asyncio.Queue()
    seen: list[str] = []

    async def handle(j: Job) -> None:
        seen.append(j.payload)

    await q.put(Job("a", "p"))
    await q.put(None)
    t = asyncio.create_task(worker(q, handle))
    await q.join()
    await t
    assert seen == ["p"]
