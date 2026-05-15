from __future__ import annotations

from dataclasses import dataclass

from kafka_consumer_demo.processor import (
    DecodedMessage,
    dead_letter_ids,
    decode_record,
    process_poll_result,
)


@dataclass
class _FakeRecord:
    topic: str
    key: bytes | None
    value: bytes | None


def test_process_poll_result_invokes_handler() -> None:
    poll = {"tp-1": [_FakeRecord("orders", b"k1", b'{"a":1}')]}
    seen: list[DecodedMessage] = []

    def on_message(m: DecodedMessage) -> None:
        seen.append(m)

    n = process_poll_result(poll, on_message)
    assert n == 1
    assert seen[0].topic == "orders"
    assert seen[0].key_text == "k1"
    assert seen[0].value_text == '{"a":1}'


def test_decode_record_none_key_value() -> None:
    m = decode_record(_FakeRecord("t", None, None))
    assert m.key_text is None and m.value_text is None


def test_dead_letter_ids() -> None:
    ids = dead_letter_ids([DecodedMessage("t", "k", None)])
    assert ids[0].startswith("dlq:")
