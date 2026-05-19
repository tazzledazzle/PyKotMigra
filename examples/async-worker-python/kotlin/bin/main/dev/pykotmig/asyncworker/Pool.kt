package dev.pykotmig.asyncworker

import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.launch
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

data class Job(
    val jobId: String,
    val payload: String,
)

/**
 * Mirrors the Python `asyncio` worker pool: bounded concurrency over a shared queue with explicit
 * shutdown sentinels. Production Temporal workers would use `io.temporal.*` instead of this queue.
 */
suspend fun worker(
    queue: Channel<Job?>,
    process: suspend (Job) -> Unit,
) {
    while (true) {
        val job = queue.receive()
        if (job == null) {
            return
        }
        process(job)
    }
}

suspend fun runPool(
    workerCount: Int,
    jobs: List<Job>,
    process: suspend (Job) -> Unit,
) = coroutineScope {
    require(workerCount >= 1)
    val q = Channel<Job?>(Channel.UNLIMITED)
    val jobsTotal = jobs.size
    val mutex = Mutex()
    var done = 0
    val allDone = CompletableDeferred<Unit>()

    val wrapped: suspend (Job) -> Unit = { job ->
        process(job)
        mutex.withLock {
            done++
            if (done == jobsTotal) {
                allDone.complete(Unit)
            }
        }
    }

    repeat(workerCount) {
        launch {
            worker(q, wrapped)
        }
    }

    for (j in jobs) {
        q.send(j)
    }

    if (jobsTotal == 0) {
        allDone.complete(Unit)
    }
    allDone.await()

    repeat(workerCount) {
        q.send(null)
    }
}
