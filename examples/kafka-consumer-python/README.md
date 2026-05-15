# Kafka consumer (Python)

**Map:** `confluent-kafka-python` / `kafka-python` consumers → **JVM** `kafka-clients` + `kotlinx.coroutines` (DLQ patterns in Kotlin).

This demo uses **`kafka-python`** for a small poll/handler loop. Tests use fakes; a real broker is optional (see `python/README.md`).

## Layout

- `python/` — poll/handler loop + processor helpers (`uv` + `pytest`)
- `kotlin/` — `kafka-clients` runnable consumer + shared decode/DLQ helpers (`./gradlew test` / `./gradlew run`)

## Python

```bash
cd python && uv sync --extra dev && uv run pytest -q && uv run mypy src
```

## Kotlin

```bash
cd kotlin && ./gradlew test
```

Runnable consumer (requires a broker; same env vars as Python `consumer_main.py`):

```bash
cd kotlin && ./gradlew run
```

Uses `kafka-clients` with byte-array deserializers; `KafkaBytesRecord` adapts `ConsumerRecord`s into the same `decodeRecord` / `processPollResult` path as unit tests.
