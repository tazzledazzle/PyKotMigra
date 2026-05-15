"""Processor edge cases and optional consumer main wiring."""

from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import MagicMock, patch

import pytest

from kafka_consumer_demo.processor import (
    DecodedMessage,
    decode_record,
    dead_letter_ids,
    process_poll_result,
)


@dataclass
class _Rec:
    topic: str
    key: object | None
    value: object | None


def test_decode_record_rejects_non_bytes_key() -> None:
    with pytest.raises(TypeError, match="record.key"):
        decode_record(_Rec("t", "not-bytes", b"v"))


def test_decode_record_rejects_non_bytes_value() -> None:
    with pytest.raises(TypeError, match="record.value"):
        decode_record(_Rec("t", b"k", "not-bytes"))


def test_process_poll_result_empty() -> None:
    assert process_poll_result({}, lambda _m: None) == 0


def test_dead_letter_ids_multiple() -> None:
    ids = dead_letter_ids(
        [DecodedMessage("a", "k1", None), DecodedMessage(None, None, "x")]
    )
    assert len(ids) == 2
    assert "unknown" in ids[1]


def test_consumer_main_keyboard_interrupt_closes() -> None:
    import kafka_consumer_demo.consumer_main as cm

    consumer = MagicMock()
    consumer.poll.side_effect = [{}, KeyboardInterrupt()]
    with patch.object(cm, "KafkaConsumer", return_value=consumer):
        assert cm.main() == 0
    consumer.close.assert_called_once()
