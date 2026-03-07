import logging
from unittest.mock import MagicMock, call, patch

import pytest

from pryces.application.exceptions import MessageSendingFailed
from pryces.infrastructure.senders import RetryMessageSender, RetrySettings


def _make_sender(max_retries=3, base_delay=1.0, backoff_factor=2.0) -> RetryMessageSender:
    inner = MagicMock()
    settings = RetrySettings(
        max_retries=max_retries, base_delay=base_delay, backoff_factor=backoff_factor
    )
    return RetryMessageSender(inner=inner, settings=settings), inner


class TestRetryMessageSender:
    def test_success_on_first_attempt_returns_true(self):
        sender, inner = _make_sender()
        inner.send_message.return_value = True

        result = sender.send_message("hello")

        assert result is True
        inner.send_message.assert_called_once_with("hello")

    def test_non_retryable_failure_raises_immediately(self):
        sender, inner = _make_sender()
        inner.send_message.side_effect = MessageSendingFailed("bad token", retryable=False)

        with pytest.raises(MessageSendingFailed):
            sender.send_message("hello")

        inner.send_message.assert_called_once()

    def test_retryable_failure_always_fails_raises_after_max_retries(self):
        sender, inner = _make_sender(max_retries=3)
        inner.send_message.side_effect = MessageSendingFailed("timeout", retryable=True)

        with patch("pryces.infrastructure.senders.time.sleep"):
            with pytest.raises(MessageSendingFailed):
                sender.send_message("hello")

        assert inner.send_message.call_count == 4  # 1 initial + 3 retries

    def test_retryable_failure_then_success_returns_true(self):
        sender, inner = _make_sender(max_retries=3)
        inner.send_message.side_effect = [
            MessageSendingFailed("timeout", retryable=True),
            MessageSendingFailed("timeout", retryable=True),
            True,
        ]

        with patch("pryces.infrastructure.senders.time.sleep"):
            result = sender.send_message("hello")

        assert result is True
        assert inner.send_message.call_count == 3

    def test_delays_are_exponential(self):
        sender, inner = _make_sender(max_retries=3, base_delay=1.0, backoff_factor=2.0)
        inner.send_message.side_effect = MessageSendingFailed("timeout", retryable=True)

        with patch("pryces.infrastructure.senders.time.sleep") as mock_sleep:
            with pytest.raises(MessageSendingFailed):
                sender.send_message("hello")

        assert mock_sleep.call_args_list == [call(1.0), call(2.0), call(4.0)]

    def test_warning_logged_on_each_retry(self, caplog):
        sender, inner = _make_sender(max_retries=2)
        inner.send_message.side_effect = MessageSendingFailed("timeout", retryable=True)

        with patch("pryces.infrastructure.senders.time.sleep"):
            with caplog.at_level(logging.WARNING, logger="pryces.infrastructure.senders"):
                with pytest.raises(MessageSendingFailed):
                    sender.send_message("hello")

        assert caplog.text.count("retrying in") == 2

    def test_zero_max_retries_raises_immediately_on_retryable(self):
        sender, inner = _make_sender(max_retries=0)
        inner.send_message.side_effect = MessageSendingFailed("timeout", retryable=True)

        with pytest.raises(MessageSendingFailed):
            sender.send_message("hello")

        inner.send_message.assert_called_once()
