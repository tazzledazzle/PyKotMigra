package dev.pykotmig.asyncworker

import io.temporal.client.WorkflowOptions
import io.temporal.testing.TestWorkflowEnvironment
import io.temporal.worker.Worker
import io.temporal.workflow.WorkflowInterface
import io.temporal.workflow.WorkflowMethod
import org.junit.jupiter.api.Test
import kotlin.test.assertEquals

/**
 * Minimal in-memory Temporal workflow proving the Java SDK runs from this module’s tests.
 * The main pool code remains the asyncio-style queue mirror; production workers use
 * `io.temporal.worker.Worker` against a real Temporal service.
 */
@WorkflowInterface
interface DemoWorkflow {
    @WorkflowMethod
    fun execute(name: String): String
}

class DemoWorkflowImpl : DemoWorkflow {
    override fun execute(name: String): String = "Hello, $name"
}

class TemporalSmokeTest {
    @Test
    fun inMemoryWorkflow() {
        TestWorkflowEnvironment.newInstance().use { env ->
            val worker: Worker = env.newWorker("pykotmig-test-queue")
            worker.registerWorkflowImplementationTypes(DemoWorkflowImpl::class.java)
            env.start()
            val stub =
                env.workflowClient.newWorkflowStub(
                    DemoWorkflow::class.java,
                    WorkflowOptions.newBuilder().setTaskQueue("pykotmig-test-queue").build(),
                )
            assertEquals("Hello, Temporal", stub.execute("Temporal"))
        }
    }
}
