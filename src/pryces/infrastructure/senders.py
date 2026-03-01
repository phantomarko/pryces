import json
import logging
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from ..application.interfaces import MessageSender


@dataclass(frozen=True, slots=True)
class TelegramSettings:
    bot_token: str
    group_id: str


class TelegramMessageSender(MessageSender):
    _HEADERS = {"Content-Type": "application/json"}

    def __init__(self, settings: TelegramSettings) -> None:
        self._settings = settings
        self._logger = logging.getLogger(__name__)
        self._url = f"https://api.telegram.org/bot{settings.bot_token}/sendMessage"

    def send_message(self, message: str) -> bool:
        payload = json.dumps({"chat_id": self._settings.group_id, "text": message}).encode("utf-8")

        self._logger.debug(f"Sending message to Telegram group {self._settings.group_id}")

        request = urllib.request.Request(self._url, data=payload, headers=self._HEADERS)

        try:
            response = urllib.request.urlopen(request)
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            self._logger.error(f"Telegram API HTTP {e.code}: {error_body}")
            raise

        response_data = json.loads(response.read().decode("utf-8"))

        if response_data.get("ok") is True:
            self._logger.info(f"Notification sent:\n{message}")
            return True

        self._logger.error(f"Telegram API returned ok=false: {response_data}")
        return False


class FireAndForgetMessageSender(MessageSender):
    def __init__(self, inner: MessageSender) -> None:
        self._inner = inner
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._logger = logging.getLogger(__name__)

    def _send(self, message: str) -> None:
        try:
            self._inner.send_message(message)
        except Exception as e:
            self._logger.error(f"Failed to send message: {e}")

    def send_message(self, message: str) -> bool:
        self._executor.submit(self._send, message)
        return True

    def shutdown(self) -> None:
        self._executor.shutdown(wait=True)
