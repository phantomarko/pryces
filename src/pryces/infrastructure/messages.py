import json
import logging
import urllib.request
from dataclasses import dataclass

from ..application.messages import MessageSender


@dataclass(frozen=True)
class TelegramSettings:
    bot_token: str
    group_id: str


class TelegramMessageSender(MessageSender):
    def __init__(self, settings: TelegramSettings) -> None:
        self._settings = settings
        self._logger = logging.getLogger(__name__)

    def send_message(self, message: str) -> bool:
        url = f"https://api.telegram.org/bot{self._settings.bot_token}/sendMessage"
        payload = json.dumps({"chat_id": self._settings.group_id, "text": message}).encode("utf-8")

        self._logger.debug(f"Sending message to Telegram group {self._settings.group_id}")

        request = urllib.request.Request(
            url, data=payload, headers={"Content-Type": "application/json"}
        )
        response = urllib.request.urlopen(request)

        response_data = json.loads(response.read().decode("utf-8"))

        if response_data.get("ok") is True:
            self._logger.info("Message sent successfully via Telegram")
            return True

        self._logger.warning(f"Telegram API returned ok=false: {response_data}")
        return False
