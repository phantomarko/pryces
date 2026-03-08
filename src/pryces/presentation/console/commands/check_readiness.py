import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from ....application.interfaces import Logger, LoggerFactory
from ....application.use_cases.send_messages import SendMessages, SendMessagesRequest
from .base import Command, CommandMetadata, CommandResult, InputPrompt

_READY = "[READY]"
_NOT_READY = "[NOT READY]"
_WARNING = "Fix the errors above and restart the app for changes to take effect."


@dataclass(frozen=True)
class CheckResult:
    ready: bool
    message: str


class Checker(ABC):
    @abstractmethod
    def check(self) -> CheckResult:
        pass


class EnvVarsChecker(Checker):
    def check(self) -> CheckResult:
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

        extra_delay = os.environ.get("EXTRA_DELAY_IN_MINUTES", "")
        if extra_delay.strip():
            try:
                if int(extra_delay) < 0:
                    errors.append("  - EXTRA_DELAY_IN_MINUTES must be a non-negative integer")
            except ValueError:
                errors.append("  - EXTRA_DELAY_IN_MINUTES is not a valid integer")

        if errors:
            return CheckResult(
                ready=False,
                message=f"{_NOT_READY} Environment variables\n" + "\n".join(errors),
            )
        return CheckResult(ready=True, message=f"{_READY} Environment variables")


class TelegramChecker(Checker):
    def __init__(self, send_messages: SendMessages, logger: Logger) -> None:
        self._send_messages = send_messages
        self._logger = logger

    def check(self) -> CheckResult:
        try:
            request = SendMessagesRequest(
                messages=["Pryces — Stock price monitor.\nhttps://github.com/phantomarko/pryces"]
            )
            response = self._send_messages.handle(request)

            if response.successful > 0 and response.failed == 0:
                return CheckResult(ready=True, message=f"{_READY} Telegram notifications")
            else:
                return CheckResult(ready=False, message=f"{_NOT_READY} Telegram notifications")

        except Exception as e:
            self._logger.error(f"Telegram readiness check failed: {e}")
            return CheckResult(ready=False, message=f"{_NOT_READY} Telegram notifications")


class CheckReadinessCommand(Command):
    def __init__(self, checkers: list[Checker], logger_factory: LoggerFactory) -> None:
        self._checkers = checkers
        self._logger = logger_factory.get_logger(__name__)

    def get_metadata(self) -> CommandMetadata:
        return CommandMetadata(
            id="check_readiness",
            name="Check Readiness",
            description="Check if all components and configs are ready for monitoring",
        )

    def get_input_prompts(self) -> list[InputPrompt]:
        return []

    def execute(self, **kwargs) -> CommandResult:
        self._logger.info("Check Readiness command started")
        results = [checker.check() for checker in self._checkers]
        all_ready = all(r.ready for r in results)
        lines = [r.message for r in results]
        if not all_ready:
            lines.append("")
            lines.append(_WARNING)
        self._logger.info("Check Readiness command finished")
        return CommandResult(message="\n".join(lines), success=all_ready)
