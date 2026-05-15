"""Optional real-consumer entrypoint (requires running Kafka)."""

from __future__ import annotations

import os
import sys

from kafka import KafkaConsumer

from kafka_consumer_demo.processor import DecodedMessage, process_poll_result


def _print_message(m: DecodedMessage) -> None:
    print(f"topic={m.topic} key={m.key_text!r} value={m.value_text!r}", flush=True)


def main() -> int:
    bootstrap = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    topic = os.environ.get("KAFKA_TOPIC", "demo.events")
    group = os.environ.get("KAFKA_GROUP_ID", "pykotmig-kafka-demo")
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap,
        group_id=group,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        consumer_timeout_ms=5000,
    )
    try:
        while True:
            raw = consumer.poll(timeout_ms=1000)
            if not raw:
                continue
            process_poll_result(raw, _print_message)
    except KeyboardInterrupt:
        print("stopped", file=sys.stderr)
    finally:
        consumer.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
