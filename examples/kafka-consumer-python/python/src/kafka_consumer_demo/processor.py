"""Pure poll-result processing (unit-testable without a broker)."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from typing import Any, TypeAlias

# kafka-python returns TopicPartition keys; values are lists of ConsumerRecord-like objects.
PollResult: TypeAlias = Mapping[Any, list[Any]]


@dataclass(frozen=True, slots=True)
class DecodedMessage:
    """Normalized view of a consumed record."""

    topic: str | None
    key_text: str | None
    value_text: str | None


def _record_topic(record: Any) -> str | None:
    t = getattr(record, "topic", None)
    return str(t) if t is not None else None


def _record_key_value(record: Any) -> tuple[bytes | None, bytes | None]:
    key = getattr(record, "key", None)
    val = getattr(record, "value", None)
    if key is not None and not isinstance(key, bytes):
        raise TypeError("record.key must be bytes or None")
    if val is not None and not isinstance(val, bytes):
        raise TypeError("record.value must be bytes or None")
    return key, val


def decode_record(record: Any) -> DecodedMessage:
    """Decode a kafka ConsumerRecord-like object into text fields."""
    topic = _record_topic(record)
    raw_key, raw_val = _record_key_value(record)
    key_text = raw_key.decode("utf-8") if raw_key is not None else None
    value_text = raw_val.decode("utf-8") if raw_val is not None else None
    return DecodedMessage(topic=topic, key_text=key_text, value_text=value_text)


def process_poll_result(
    poll_result: PollResult,
    on_message: Callable[[DecodedMessage], None],
) -> int:
    """Invoke ``on_message`` for every record in a ``consumer.poll()`` map; return count."""
    count = 0
    for _tp, batch in poll_result.items():
        for record in batch:
            on_message(decode_record(record))
            count += 1
    return count


def dead_letter_ids(failed: Iterable[DecodedMessage]) -> list[str]:
    """Build synthetic DLQ ids for failed decodes (demo only)."""
    out: list[str] = []
    for m in failed:
        out.append(f"dlq:{m.topic or 'unknown'}:{m.key_text or ''}")
    return out
