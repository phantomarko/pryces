import json
import urllib.error
import urllib.request
from dataclasses import dataclass

from ..application.interfaces import LoggerFactory
from .senders import TelegramSettings


@dataclass(frozen=True, slots=True)
class BotUpdate:
    update_id: int
    chat_id: str
    text: str


class TelegramUpdatePoller:
    def __init__(self, settings: TelegramSettings, logger_factory: LoggerFactory) -> None:
        self._logger = logger_factory.get_logger(__name__)
        self._url = f"https://api.telegram.org/bot{settings.bot_token}/getUpdates"

    def get_updates(self, offset: int) -> list[BotUpdate]:
        url = f"{self._url}?offset={offset}&timeout=30"
        request = urllib.request.Request(url)

        try:
            response = urllib.request.urlopen(request, timeout=35)
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            self._logger.error(f"Telegram API HTTP {e.code}: {error_body}")
            return []
        except (urllib.error.URLError, OSError) as e:
            self._logger.error(f"Telegram API network error: {e}")
            return []

        data = json.loads(response.read().decode("utf-8"))
        if not data.get("ok"):
            self._logger.error(f"Telegram API returned ok=false: {data}")
            return []

        updates = []
        for item in data.get("result", []):
            message = item.get("message") or {}
            text = message.get("text")
            chat = message.get("chat") or {}
            chat_id = chat.get("id")
            if text is None or chat_id is None:
                continue
            updates.append(
                BotUpdate(
                    update_id=item["update_id"],
                    chat_id=str(chat_id),
                    text=text,
                )
            )

        return updates
