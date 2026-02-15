import logging
import os
from pathlib import Path

from ....application.use_cases.send_messages import SendMessages, SendMessagesRequest
from .base import Command, CommandMetadata, InputPrompt

_READY = "[READY]"
_NOT_READY = "[NOT READY]"
_WARNING = "Fix the errors above and restart the app for changes to take effect."


class CheckReadinessCommand(Command):
    def __init__(self, send_messages_use_case: SendMessages) -> None:
        self._send_messages = send_messages_use_case
        self._logger = logging.getLogger(__name__)
        self._all_ready = True

    def get_metadata(self) -> CommandMetadata:
        return CommandMetadata(
            id="check_readiness",
            name="Check Readiness",
            description="Check if all components and configs are ready for monitoring",
        )

    def get_input_prompts(self) -> list[InputPrompt]:
        return []

    def execute(self, **kwargs) -> str:
        self._logger.info("Check Readiness command started")
        self._all_ready = True
        results = [
            self._check_env(),
            self._check_telegram(),
        ]
        if not self._all_ready:
            results.append("")
            results.append(_WARNING)
        self._logger.info("Check Readiness command finished")
        return "\n".join(results)

    def _check_env(self) -> str:
        errors = []

        for var in ("TELEGRAM_BOT_TOKEN", "TELEGRAM_GROUP_ID"):
            value = os.environ.get(var, "")
            if not value.strip():
                errors.append(f"  - {var} is missing or empty")

        max_workers = os.environ.get("MAX_FETCH_WORKERS", "")
        try:
            if int(max_workers) <= 0:
                errors.append("  - MAX_FETCH_WORKERS must be a positive integer")
        except ValueError:
            errors.append("  - MAX_FETCH_WORKERS is missing or not a valid integer")

        logs_dir = os.environ.get("LOGS_DIRECTORY", "")
        if logs_dir and not Path(logs_dir).is_dir():
            errors.append(f"  - LOGS_DIRECTORY is not a valid directory: {logs_dir}")

        if errors:
            self._all_ready = False
            return f"{_NOT_READY} Environment variables\n" + "\n".join(errors)
        return f"{_READY} Environment variables"

    def _check_telegram(self) -> str:
        try:
            request = SendMessagesRequest(messages=["Hello!\nThis is a test message."])
            response = self._send_messages.handle(request)

            if response.successful > 0 and response.failed == 0:
                return f"{_READY} Telegram notifications"
            else:
                self._all_ready = False
                return f"{_NOT_READY} Telegram notifications"

        except Exception as e:
            self._logger.error(f"Telegram readiness check failed: {e}")
            self._all_ready = False
            return f"{_NOT_READY} Telegram notifications"
