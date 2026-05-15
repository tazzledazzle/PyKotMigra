# kafka-consumer-demo

Install: `uv sync --extra dev`

Optional local broker: `docker run --rm -p 9092:9092 apache/kafka:3.7.0` (or your cluster) then set `KAFKA_BOOTSTRAP_SERVERS`.

Core logic is in `src/kafka_consumer_demo/processor.py` (testable without a broker). `consumer_main.py` wraps `kafka.KafkaConsumer`.
