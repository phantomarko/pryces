import json
import urllib.error
from unittest.mock import Mock, patch

from pryces.infrastructure.receivers import BotUpdate, TelegramUpdatePoller
from pryces.infrastructure.senders import TelegramSettings


def make_poller() -> TelegramUpdatePoller:
    settings = TelegramSettings(bot_token="test-token", group_id="123")
    return TelegramUpdatePoller(settings=settings, logger_factory=Mock())


def make_response(result: list) -> Mock:
    data = json.dumps({"ok": True, "result": result}).encode("utf-8")
    response = Mock()
    response.read.return_value = data
    return response


class TestTelegramUpdatePoller:

    @patch("pryces.infrastructure.receivers.urllib.request.urlopen")
    def test_parses_updates_correctly(self, mock_urlopen):
        mock_urlopen.return_value = make_response(
            [
                {
                    "update_id": 1,
                    "message": {"chat": {"id": 456}, "text": "/help"},
                },
                {
                    "update_id": 2,
                    "message": {"chat": {"id": 789}, "text": "/targets AAPL"},
                },
            ]
        )
        poller = make_poller()

        updates = poller.get_updates(0)

        assert len(updates) == 2
        assert updates[0] == BotUpdate(update_id=1, chat_id="456", text="/help")
        assert updates[1] == BotUpdate(update_id=2, chat_id="789", text="/targets AAPL")

    @patch("pryces.infrastructure.receivers.urllib.request.urlopen")
    def test_skips_updates_without_text(self, mock_urlopen):
        mock_urlopen.return_value = make_response(
            [
                {
                    "update_id": 1,
                    "message": {"chat": {"id": 456}},
                },
                {
                    "update_id": 2,
                    "message": {"chat": {"id": 456}, "text": "/help"},
                },
            ]
        )
        poller = make_poller()

        updates = poller.get_updates(0)

        assert len(updates) == 1
        assert updates[0].text == "/help"

    @patch("pryces.infrastructure.receivers.urllib.request.urlopen")
    def test_skips_updates_without_message(self, mock_urlopen):
        mock_urlopen.return_value = make_response(
            [
                {"update_id": 1},
                {
                    "update_id": 2,
                    "message": {"chat": {"id": 456}, "text": "/help"},
                },
            ]
        )
        poller = make_poller()

        updates = poller.get_updates(0)

        assert len(updates) == 1

    @patch("pryces.infrastructure.receivers.urllib.request.urlopen")
    def test_returns_empty_list_on_http_error(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="", code=500, msg="", hdrs=None, fp=Mock(read=lambda: b"error")
        )
        poller = make_poller()

        updates = poller.get_updates(0)

        assert updates == []

    @patch("pryces.infrastructure.receivers.urllib.request.urlopen")
    def test_returns_empty_list_on_network_error(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.URLError("connection refused")
        poller = make_poller()

        updates = poller.get_updates(0)

        assert updates == []

    @patch("pryces.infrastructure.receivers.urllib.request.urlopen")
    def test_returns_empty_list_when_ok_is_false(self, mock_urlopen):
        data = json.dumps({"ok": False, "description": "Unauthorized"}).encode("utf-8")
        response = Mock()
        response.read.return_value = data
        mock_urlopen.return_value = response
        poller = make_poller()

        updates = poller.get_updates(0)

        assert updates == []

    @patch("pryces.infrastructure.receivers.urllib.request.urlopen")
    def test_passes_offset_in_url(self, mock_urlopen):
        mock_urlopen.return_value = make_response([])
        poller = make_poller()

        poller.get_updates(42)

        call_args = mock_urlopen.call_args
        request = call_args[0][0]
        assert "offset=42" in request.full_url

    @patch("pryces.infrastructure.receivers.urllib.request.urlopen")
    def test_converts_chat_id_to_string(self, mock_urlopen):
        mock_urlopen.return_value = make_response(
            [
                {
                    "update_id": 1,
                    "message": {"chat": {"id": -1001234567890}, "text": "hi"},
                },
            ]
        )
        poller = make_poller()

        updates = poller.get_updates(0)

        assert updates[0].chat_id == "-1001234567890"
