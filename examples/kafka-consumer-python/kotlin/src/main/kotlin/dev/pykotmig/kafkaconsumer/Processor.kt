package dev.pykotmig.kafkaconsumer

/**
 * Minimal record shape matching `kafka-python` consumer records used by the Python demo.
 *
 * Production consumers use `org.apache.kafka.clients.consumer.ConsumerRecord` from
 * `kafka-clients` with the same field semantics.
 */
interface ConsumerRecordLike {
    val topic: Any?
    val key: Any?
    val value: Any?
}

data class DecodedMessage(
    val topic: String?,
    val keyText: String?,
    val valueText: String?,
)

private fun recordTopic(record: ConsumerRecordLike): String? {
    val t = record.topic ?: return null
    return t.toString()
}

private fun recordKeyValue(record: ConsumerRecordLike): Pair<ByteArray?, ByteArray?> {
    val key = record.key
    val value = record.value
    if (key != null && key !is ByteArray) {
        throw IllegalArgumentException("record.key must be bytes or null")
    }
    if (value != null && value !is ByteArray) {
        throw IllegalArgumentException("record.value must be bytes or null")
    }
    @Suppress("UNCHECKED_CAST")
    return key as ByteArray? to value as ByteArray?
}

fun decodeRecord(record: ConsumerRecordLike): DecodedMessage {
    val topic = recordTopic(record)
    val (rawKey, rawVal) = recordKeyValue(record)
    val keyText = rawKey?.let { String(it, Charsets.UTF_8) }
    val valueText = rawVal?.let { String(it, Charsets.UTF_8) }
    return DecodedMessage(topic = topic, keyText = keyText, valueText = valueText)
}

fun processPollResult(
    pollResult: Map<*, List<ConsumerRecordLike>>,
    onMessage: (DecodedMessage) -> Unit,
): Int {
    var count = 0
    for ((_, batch) in pollResult) {
        for (record in batch) {
            onMessage(decodeRecord(record))
            count++
        }
    }
    return count
}

fun deadLetterIds(failed: Iterable<DecodedMessage>): List<String> =
    failed.map { m ->
        "dlq:${m.topic ?: "unknown"}:${m.keyText ?: ""}"
    }
