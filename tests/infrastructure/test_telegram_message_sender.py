import json
import urllib.error
from unittest.mock import Mock, patch

import pytest

from pryces.application.exceptions import MessageSendingFailed
from pryces.infrastructure.senders import TelegramMessageSender, TelegramSettings


def make_sender() -> TelegramMessageSender:
    settings = TelegramSettings(bot_token="test-token", group_id="123")
    return TelegramMessageSender(settings=settings, logger_factory=Mock())


def make_ok_response() -> Mock:
    data = json.dumps({"ok": True, "result": {}}).encode("utf-8")
    response = Mock()
    response.read.return_value = data
    return response


def make_error_response(error_code: int | None = None) -> Mock:
    payload: dict = {"ok": False, "description": "error"}
    if error_code is not None:
        payload["error_code"] = error_code
    data = json.dumps(payload).encode("utf-8")
    response = Mock()
    response.read.return_value = data
    return response


class TestTelegramMessageSender:

    @patch("pryces.infrastructure.senders.urllib.request.urlopen")
    def test_returns_true_on_ok_response(self, mock_urlopen):
        mock_urlopen.return_value = make_ok_response()
        sender = make_sender()

        result = sender.send_message("hello")

        assert result is True

    @patch("pryces.infrastructure.senders.urllib.request.urlopen")
    def test_ok_false_with_429_is_retryable(self, mock_urlopen):
        mock_urlopen.return_value = make_error_response(error_code=429)
        sender = make_sender()

        with pytest.raises(MessageSendingFailed) as exc_info:
            sender.send_message("hello")

        assert exc_info.value.retryable is True

    @patch("pryces.infrastructure.senders.urllib.request.urlopen")
    def test_ok_false_with_500_is_retryable(self, mock_urlopen):
        mock_urlopen.return_value = make_error_response(error_code=500)
        sender = make_sender()

        with pytest.raises(MessageSendingFailed) as exc_info:
            sender.send_message("hello")

        assert exc_info.value.retryable is True

    @patch("pryces.infrastructure.senders.urllib.request.urlopen")
    def test_ok_false_with_400_is_not_retryable(self, mock_urlopen):
        mock_urlopen.return_value = make_error_response(error_code=400)
        sender = make_sender()

        with pytest.raises(MessageSendingFailed) as exc_info:
            sender.send_message("hello")

        assert exc_info.value.retryable is False

    @patch("pryces.infrastructure.senders.urllib.request.urlopen")
    def test_ok_false_without_error_code_is_not_retryable(self, mock_urlopen):
        mock_urlopen.return_value = make_error_response()
        sender = make_sender()

        with pytest.raises(MessageSendingFailed) as exc_info:
            sender.send_message("hello")

        assert exc_info.value.retryable is False

    @patch("pryces.infrastructure.senders.urllib.request.urlopen")
    def test_http_429_is_retryable(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="",
            code=429,
            msg="Too Many Requests",
            hdrs=None,
            fp=Mock(read=lambda: b"rate limited"),
        )
        sender = make_sender()

        with pytest.raises(MessageSendingFailed) as exc_info:
            sender.send_message("hello")

        assert exc_info.value.retryable is True

    @patch("pryces.infrastructure.senders.urllib.request.urlopen")
    def test_http_500_is_retryable(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="", code=500, msg="Internal Server Error", hdrs=None, fp=Mock(read=lambda: b"error")
        )
        sender = make_sender()

        with pytest.raises(MessageSendingFailed) as exc_info:
            sender.send_message("hello")

        assert exc_info.value.retryable is True

    @patch("pryces.infrastructure.senders.urllib.request.urlopen")
    def test_http_400_is_not_retryable(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="", code=400, msg="Bad Request", hdrs=None, fp=Mock(read=lambda: b"bad request")
        )
        sender = make_sender()

        with pytest.raises(MessageSendingFailed) as exc_info:
            sender.send_message("hello")

        assert exc_info.value.retryable is False

    @patch("pryces.infrastructure.senders.urllib.request.urlopen")
    def test_network_error_is_retryable(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.URLError("connection refused")
        sender = make_sender()

        with pytest.raises(MessageSendingFailed) as exc_info:
            sender.send_message("hello")

        assert exc_info.value.retryable is True
