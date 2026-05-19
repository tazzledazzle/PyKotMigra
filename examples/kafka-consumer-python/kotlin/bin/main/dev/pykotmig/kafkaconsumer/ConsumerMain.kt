package dev.pykotmig.kafkaconsumer

import org.apache.kafka.clients.consumer.ConsumerConfig
import org.apache.kafka.clients.consumer.KafkaConsumer
import org.apache.kafka.common.serialization.ByteArrayDeserializer
import java.time.Duration
import java.util.Properties

private fun env(name: String, default: String): String = System.getenv(name)?.takeIf { it.isNotBlank() } ?: default

fun main() {
    val bootstrap = env("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    val topic = env("KAFKA_TOPIC", "demo.events")
    val group = env("KAFKA_GROUP_ID", "pykotmig-kafka-demo")
    val props =
        Properties().apply {
            put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrap)
            put(ConsumerConfig.GROUP_ID_CONFIG, group)
            put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest")
            put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, "true")
            put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, ByteArrayDeserializer::class.java.name)
            put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, ByteArrayDeserializer::class.java.name)
            put(ConsumerConfig.CONNECTIONS_MAX_IDLE_MS_CONFIG, "10000")
        }

    KafkaConsumer<ByteArray?, ByteArray?>(props).use { consumer ->
        consumer.subscribe(listOf(topic))
        while (true) {
            val batch = consumer.poll(Duration.ofMillis(1000))
            if (batch.isEmpty) {
                continue
            }
            processPollResult(batch.toPollResult()) { m ->
                println("topic=${m.topic} key=${m.keyText} value=${m.valueText}")
            }
        }
    }
}
