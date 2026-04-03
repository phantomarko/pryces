import logging
from unittest.mock import MagicMock, Mock

from pryces.application.exceptions import MessageSendingFailed
from pryces.infrastructure.logging import PythonLoggerFactory
from pryces.infrastructure.senders import FireAndForgetMessageSender


class TestFireAndForgetMessageSender:
    def _create_sender(self, inner: MagicMock, logger_factory=None) -> FireAndForgetMessageSender:
        sender = FireAndForgetMessageSender(inner=inner, logger_factory=logger_factory or Mock())
        return sender

    def test_send_message_returns_true(self):
        inner = MagicMock()
        sender = self._create_sender(inner)

        result = sender.send_message("hello")
        sender.shutdown()

        assert result is True

    def test_send_message_delegates_to_inner(self):
        inner = MagicMock()
        sender = self._create_sender(inner)

        sender.send_message("hello")
        sender.shutdown()

        inner.send_message.assert_called_once_with("hello")

    def test_multiple_messages_are_all_delivered(self):
        inner = MagicMock()
        sender = self._create_sender(inner)

        sender.send_message("first")
        sender.send_message("second")
        sender.send_message("third")
        sender.shutdown()

        assert inner.send_message.call_count == 3
        inner.send_message.assert_any_call("first")
        inner.send_message.assert_any_call("second")
        inner.send_message.assert_any_call("third")

    def test_inner_exception_is_caught_and_logged(self, caplog):
        inner = MagicMock()
        inner.send_message.side_effect = MessageSendingFailed("connection failed")
        sender = self._create_sender(inner, logger_factory=PythonLoggerFactory())

        result = sender.send_message("hello")
        sender.shutdown()

        assert result is True
        assert "Failed to send message" in caplog.text

    def test_inner_exception_does_not_prevent_subsequent_messages(self):
        inner = MagicMock()
        inner.send_message.side_effect = [MessageSendingFailed("fail"), None]
        sender = self._create_sender(inner)

        sender.send_message("first")
        sender.send_message("second")
        sender.shutdown()

        assert inner.send_message.call_count == 2

    def test_shutdown_waits_for_pending_messages(self):
        inner = MagicMock()
        sender = self._create_sender(inner)

        sender.send_message("hello")
        sender.shutdown()

        inner.send_message.assert_called_once_with("hello")

    def test_shutdown_does_not_propagate_exception_raised_by_inner(self, caplog):
        inner = MagicMock()
        inner.send_message.side_effect = RuntimeError("unexpected failure")
        sender = self._create_sender(inner, logger_factory=PythonLoggerFactory())

        sender.send_message("hello")

        # shutdown() must return normally even when the background task raised
        sender.shutdown()

        assert "Failed to send message" in caplog.text
