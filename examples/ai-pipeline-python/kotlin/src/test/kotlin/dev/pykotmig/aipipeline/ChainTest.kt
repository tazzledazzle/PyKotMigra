package dev.pykotmig.aipipeline

import org.junit.jupiter.api.Test
import kotlin.test.assertTrue

class ChainTest {
    @Test
    fun pipelineRuns() {
        val chain = buildDemoPipeline()
        val out = chain(mapOf("query" to "  hello world  "))
        val answer = out["answer"] as String
        assertTrue(answer.startsWith("q='hello world'"))
    }
}
