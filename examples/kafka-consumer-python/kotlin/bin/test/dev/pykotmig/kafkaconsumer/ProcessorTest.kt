package dev.pykotmig.kafkaconsumer

import org.apache.kafka.clients.consumer.ConsumerRecord
import org.apache.kafka.common.TopicPartition
import org.junit.jupiter.api.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

private data class FakeRecord(
    override val topic: String,
    override val key: ByteArray?,
    override val value: ByteArray?,
) : ConsumerRecordLike

class ProcessorTest {
    @Test
    fun processPollResultInvokesHandler() {
        val poll = mapOf("tp-1" to listOf(FakeRecord("orders", "k1".toByteArray(), """{"a":1}""".toByteArray())))
        val seen = mutableListOf<DecodedMessage>()
        val n =
            processPollResult(poll) { m ->
                seen.add(m)
            }
        assertEquals(1, n)
        assertEquals("orders", seen[0].topic)
        assertEquals("k1", seen[0].keyText)
        assertEquals("""{"a":1}""", seen[0].valueText)
    }

    @Test
    fun decodeRecordNoneKeyValue() {
        val m = decodeRecord(FakeRecord("t", null, null))
        assertEquals(null, m.keyText)
        assertEquals(null, m.valueText)
    }

    @Test
    fun deadLetterIds() {
        val ids = deadLetterIds(listOf(DecodedMessage("t", "k", null)))
        assertTrue(ids[0].startsWith("dlq:"))
    }

    @Test
    fun kafkaBytesRecordThroughProcessor() {
        val r = ConsumerRecord("orders", 0, 0L, "k1".toByteArray(), """{"a":1}""".toByteArray())
        val poll = mapOf(TopicPartition("orders", 0) to listOf(KafkaBytesRecord(r)))
        val seen = mutableListOf<DecodedMessage>()
        val n =
            processPollResult(poll) { m ->
                seen.add(m)
            }
        assertEquals(1, n)
        assertEquals("orders", seen[0].topic)
        assertEquals("k1", seen[0].keyText)
        assertEquals("""{"a":1}""", seen[0].valueText)
    }
}
