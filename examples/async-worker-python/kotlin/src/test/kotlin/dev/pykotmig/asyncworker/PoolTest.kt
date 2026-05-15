package dev.pykotmig.asyncworker

import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Test
import kotlin.test.assertEquals

class PoolTest {
    @Test
    fun runPoolProcessesAllJobs() =
        runTest {
            val results = mutableListOf<String>()
            runPool(2, listOf(Job("1", "a"), Job("2", "b"), Job("3", "c"))) { j ->
                results.add(j.payload)
            }
            assertEquals(listOf("a", "b", "c"), results.sorted())
        }

    @Test
    fun workerStopsOnSentinel() =
        runTest {
            val q = Channel<Job?>(Channel.UNLIMITED)
            val seen = mutableListOf<String>()
            val workerJob =
                launch {
                    worker(q) { j ->
                        seen.add(j.jobId)
                    }
                }
            q.send(Job("x", "p"))
            q.send(null)
            workerJob.join()
            assertEquals(listOf("x"), seen)
        }
}
