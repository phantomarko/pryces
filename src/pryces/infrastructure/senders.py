import json
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from ..application.exceptions import MessageSendingFailed
from ..application.interfaces import LoggerFactory, MessageSender


@dataclass(frozen=True, slots=True)
class TelegramSettings:
    bot_token: str
    group_id: str


class TelegramMessageSender(MessageSender):
    _HEADERS = {"Content-Type": "application/json"}

    def __init__(self, settings: TelegramSettings, logger_factory: LoggerFactory) -> None:
        self._settings = settings
        self._logger = logger_factory.get_logger(__name__)
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
            retryable = e.code == 429 or e.code >= 500
            raise MessageSendingFailed(f"HTTP {e.code}: {error_body}", retryable=retryable) from e
        except (urllib.error.URLError, OSError) as e:
            self._logger.error(f"Telegram API network error: {e}")
            raise MessageSendingFailed(f"Network error: {e}", retryable=True) from e

        response_data = json.loads(response.read().decode("utf-8"))

        if response_data.get("ok") is True:
            self._logger.info(f"Notification sent:\n{message}")
            return True

        error_code = response_data.get("error_code", 0)
        retryable = error_code == 429 or error_code >= 500
        self._logger.error(f"Telegram API returned ok=false: {response_data}")
        raise MessageSendingFailed(f"ok=false: {response_data}", retryable=retryable)


@dataclass(frozen=True, slots=True)
class RetrySettings:
    max_retries: int
    base_delay: float
    backoff_factor: float


class RetryMessageSender(MessageSender):
    def __init__(
        self, inner: MessageSender, settings: RetrySettings, logger_factory: LoggerFactory
    ) -> None:
        self._inner = inner
        self._settings = settings
        self._logger = logger_factory.get_logger(__name__)

    def send_message(self, message: str) -> bool:
        attempt = 0
        while True:
            try:
                return self._inner.send_message(message)
            except MessageSendingFailed as e:
                if not e.retryable or attempt >= self._settings.max_retries:
                    raise
                delay = self._settings.base_delay * (self._settings.backoff_factor**attempt)
                self._logger.warning(
                    f"Send failed (attempt {attempt + 1}/{self._settings.max_retries + 1}), "
                    f"retrying in {delay}s: {e}"
                )
                time.sleep(delay)
                attempt += 1


class FireAndForgetMessageSender(MessageSender):
    def __init__(self, inner: MessageSender, logger_factory: LoggerFactory) -> None:
        self._inner = inner
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._logger = logger_factory.get_logger(__name__)

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
