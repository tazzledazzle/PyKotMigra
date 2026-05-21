"""Cover optional Kafka consumer entrypoint (mocked broker)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from kafka_consumer_demo import consumer_main
from kafka_consumer_demo.processor import DecodedMessage


def test_print_message(capsys: pytest.CaptureFixture[str]) -> None:
    consumer_main._print_message(DecodedMessage(topic="t", key_text="k", value_text="v"))
    out = capsys.readouterr().out
    assert "topic=t" in out and "key='k'" in out


def test_main_poll_loop_and_interrupt() -> None:
    consumer = MagicMock()
    consumer.poll.side_effect = [{}, KeyboardInterrupt()]
    with (
        patch.dict("os.environ", {}, clear=False),
        patch("kafka_consumer_demo.consumer_main.KafkaConsumer", return_value=consumer),
    ):
        code = consumer_main.main()
    assert code == 0
    consumer.close.assert_called_once()


def test_main_skips_empty_poll() -> None:
    consumer = MagicMock()
    consumer.poll.side_effect = [None, KeyboardInterrupt()]
    with patch("kafka_consumer_demo.consumer_main.KafkaConsumer", return_value=consumer):
        consumer_main.main()
    assert consumer.poll.call_count >= 2


def test_main_module_exit() -> None:
    import runpy

    consumer = MagicMock()
    consumer.poll.side_effect = KeyboardInterrupt()
    with patch("kafka.KafkaConsumer", return_value=consumer):
        with pytest.raises(SystemExit) as exc:
            runpy.run_module("kafka_consumer_demo.consumer_main", run_name="__main__")
    assert exc.value.code == 0
