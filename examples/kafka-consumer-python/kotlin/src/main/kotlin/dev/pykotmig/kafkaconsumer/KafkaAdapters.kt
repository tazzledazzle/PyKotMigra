package dev.pykotmig.kafkaconsumer

import org.apache.kafka.clients.consumer.ConsumerRecord
import org.apache.kafka.clients.consumer.ConsumerRecords
import org.apache.kafka.common.TopicPartition

/**
 * Wraps a JVM [ConsumerRecord] so it can flow through [decodeRecord] / [processPollResult].
 */
class KafkaBytesRecord(
    private val record: ConsumerRecord<ByteArray?, ByteArray?>,
) : ConsumerRecordLike {
    override val topic: Any?
        get() = record.topic()

    override val key: Any?
        get() = record.key()

    override val value: Any?
        get() = record.value()
}

fun ConsumerRecords<ByteArray?, ByteArray?>.toPollResult(): Map<TopicPartition, List<ConsumerRecordLike>> {
    val out = LinkedHashMap<TopicPartition, MutableList<ConsumerRecordLike>>()
    for (record in this) {
        val tp = TopicPartition(record.topic(), record.partition())
        out.getOrPut(tp) { mutableListOf() }.add(KafkaBytesRecord(record))
    }
    return out
}
