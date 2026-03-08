from unittest.mock import Mock, patch

import pytest

from pryces.application.interfaces import Logger, MessageSender
from pryces.application.use_cases.send_messages import SendMessages
from pryces.presentation.console.commands.base import CommandMetadata
from pryces.presentation.console.commands.check_readiness import (
    CheckReadinessCommand,
    CheckResult,
    Checker,
    EnvVarsChecker,
    TelegramChecker,
)


class TestCheckReadinessCommand:

    def _make_checker(self, ready: bool, message: str) -> Checker:
        checker = Mock(spec=Checker)
        checker.check.return_value = CheckResult(ready=ready, message=message)
        return checker

    def test_get_metadata_returns_correct_metadata(self):
        command = CheckReadinessCommand(checkers=[], logger_factory=Mock())

        metadata = command.get_metadata()

        assert isinstance(metadata, CommandMetadata)
        assert metadata.id == "check_readiness"
        assert metadata.name == "Check Readiness"
        assert (
            metadata.description == "Check if all components and configs are ready for monitoring"
        )

    def test_get_input_prompts_returns_empty_list(self):
        command = CheckReadinessCommand(checkers=[], logger_factory=Mock())

        assert command.get_input_prompts() == []

    def test_execute_all_ready_no_warning(self):
        checkers = [
            self._make_checker(ready=True, message="[READY] A"),
            self._make_checker(ready=True, message="[READY] B"),
        ]
        command = CheckReadinessCommand(checkers=checkers, logger_factory=Mock())

        result = command.execute()

        assert result.message == "[READY] A\n[READY] B"
        assert result.success is True
        assert "restart the app" not in result.message

    def test_execute_any_failed_appends_warning(self):
        checkers = [
            self._make_checker(ready=False, message="[NOT READY] A"),
            self._make_checker(ready=True, message="[READY] B"),
        ]
        command = CheckReadinessCommand(checkers=checkers, logger_factory=Mock())

        result = command.execute()

        assert result.success is False
        assert result.message.endswith(
            "Fix the errors above and restart the app for changes to take effect."
        )

    def test_execute_preserves_checker_message_order(self):
        checkers = [
            self._make_checker(ready=True, message="[READY] First"),
            self._make_checker(ready=False, message="[NOT READY] Second"),
        ]
        command = CheckReadinessCommand(checkers=checkers, logger_factory=Mock())

        result = command.execute()

        assert result.message.index("[READY] First") < result.message.index("[NOT READY] Second")

    def test_execute_calls_every_checker(self):
        checkers = [
            self._make_checker(ready=True, message="[READY] A"),
            self._make_checker(ready=True, message="[READY] B"),
        ]
        command = CheckReadinessCommand(checkers=checkers, logger_factory=Mock())

        command.execute()

        for checker in checkers:
            checker.check.assert_called_once()


class TestEnvVarsChecker:

    def setup_method(self):
        self.checker = EnvVarsChecker()

    @patch.dict(
        "os.environ",
        {
            "TELEGRAM_BOT_TOKEN": "token",
            "TELEGRAM_GROUP_ID": "123",
            "MAX_FETCH_WORKERS": "4",
        },
        clear=True,
    )
    def test_ready_when_required_vars_valid(self):
        result = self.checker.check()

        assert result.ready is True
        assert result.message == "[READY] Environment variables"

    @patch.dict(
        "os.environ",
        {
            "TELEGRAM_BOT_TOKEN": "token",
            "TELEGRAM_GROUP_ID": "123",
            "MAX_FETCH_WORKERS": "4",
            "LOGS_DIRECTORY": "/tmp",
        },
        clear=True,
    )
    def test_ready_when_logs_directory_exists(self):
        result = self.checker.check()

        assert result.ready is True

    @patch.dict("os.environ", {"MAX_FETCH_WORKERS": "4"}, clear=True)
    def test_not_ready_when_telegram_vars_missing(self):
        result = self.checker.check()

        assert result.ready is False
        assert "TELEGRAM_BOT_TOKEN is missing or empty" in result.message
        assert "TELEGRAM_GROUP_ID is missing or empty" in result.message

    @patch.dict(
        "os.environ",
        {"TELEGRAM_BOT_TOKEN": "  ", "TELEGRAM_GROUP_ID": "", "MAX_FETCH_WORKERS": "4"},
        clear=True,
    )
    def test_not_ready_when_telegram_vars_blank(self):
        result = self.checker.check()

        assert result.ready is False
        assert "TELEGRAM_BOT_TOKEN is missing or empty" in result.message
        assert "TELEGRAM_GROUP_ID is missing or empty" in result.message

    @patch.dict(
        "os.environ",
        {"TELEGRAM_BOT_TOKEN": "token", "TELEGRAM_GROUP_ID": "123", "MAX_FETCH_WORKERS": "abc"},
        clear=True,
    )
    def test_not_ready_when_max_fetch_workers_not_integer(self):
        result = self.checker.check()

        assert result.ready is False
        assert "MAX_FETCH_WORKERS is missing or not a valid integer" in result.message

    @patch.dict(
        "os.environ",
        {"TELEGRAM_BOT_TOKEN": "token", "TELEGRAM_GROUP_ID": "123"},
        clear=True,
    )
    def test_not_ready_when_max_fetch_workers_missing(self):
        result = self.checker.check()

        assert result.ready is False
        assert "MAX_FETCH_WORKERS is missing or not a valid integer" in result.message

    @patch.dict(
        "os.environ",
        {"TELEGRAM_BOT_TOKEN": "token", "TELEGRAM_GROUP_ID": "123", "MAX_FETCH_WORKERS": "0"},
        clear=True,
    )
    def test_not_ready_when_max_fetch_workers_zero(self):
        result = self.checker.check()

        assert result.ready is False
        assert "MAX_FETCH_WORKERS must be a positive integer" in result.message

    @patch.dict(
        "os.environ",
        {"TELEGRAM_BOT_TOKEN": "token", "TELEGRAM_GROUP_ID": "123", "MAX_FETCH_WORKERS": "-1"},
        clear=True,
    )
    def test_not_ready_when_max_fetch_workers_negative(self):
        result = self.checker.check()

        assert result.ready is False
        assert "MAX_FETCH_WORKERS must be a positive integer" in result.message

    @patch.dict(
        "os.environ",
        {
            "TELEGRAM_BOT_TOKEN": "token",
            "TELEGRAM_GROUP_ID": "123",
            "MAX_FETCH_WORKERS": "4",
            "LOGS_DIRECTORY": "/nonexistent/path/that/does/not/exist",
        },
        clear=True,
    )
    def test_not_ready_when_logs_directory_not_exists(self):
        result = self.checker.check()

        assert result.ready is False
        assert "LOGS_DIRECTORY is not a valid directory" in result.message

    @patch.dict(
        "os.environ",
        {
            "TELEGRAM_BOT_TOKEN": "token",
            "TELEGRAM_GROUP_ID": "123",
            "MAX_FETCH_WORKERS": "4",
            "LOGS_DIRECTORY": "",
        },
        clear=True,
    )
    def test_ready_when_logs_directory_empty(self):
        result = self.checker.check()

        assert result.ready is True

    @patch.dict(
        "os.environ",
        {
            "TELEGRAM_BOT_TOKEN": "token",
            "TELEGRAM_GROUP_ID": "123",
            "MAX_FETCH_WORKERS": "4",
            "EXTRA_DELAY_IN_MINUTES": "0",
        },
        clear=True,
    )
    def test_ready_when_extra_delay_is_zero(self):
        result = self.checker.check()

        assert result.ready is True

    @patch.dict(
        "os.environ",
        {
            "TELEGRAM_BOT_TOKEN": "token",
            "TELEGRAM_GROUP_ID": "123",
            "MAX_FETCH_WORKERS": "4",
            "EXTRA_DELAY_IN_MINUTES": "5",
        },
        clear=True,
    )
    def test_ready_when_extra_delay_is_positive(self):
        result = self.checker.check()

        assert result.ready is True

    @patch.dict(
        "os.environ",
        {
            "TELEGRAM_BOT_TOKEN": "token",
            "TELEGRAM_GROUP_ID": "123",
            "MAX_FETCH_WORKERS": "4",
            "EXTRA_DELAY_IN_MINUTES": "-1",
        },
        clear=True,
    )
    def test_not_ready_when_extra_delay_is_negative(self):
        result = self.checker.check()

        assert result.ready is False
        assert "EXTRA_DELAY_IN_MINUTES must be a non-negative integer" in result.message

    @patch.dict(
        "os.environ",
        {
            "TELEGRAM_BOT_TOKEN": "token",
            "TELEGRAM_GROUP_ID": "123",
            "MAX_FETCH_WORKERS": "4",
            "EXTRA_DELAY_IN_MINUTES": "abc",
        },
        clear=True,
    )
    def test_not_ready_when_extra_delay_is_not_integer(self):
        result = self.checker.check()

        assert result.ready is False
        assert "EXTRA_DELAY_IN_MINUTES is not a valid integer" in result.message


class TestTelegramChecker:

    def setup_method(self):
        self.mock_sender = Mock(spec=MessageSender)
        self.checker = TelegramChecker(
            send_messages=SendMessages(sender=self.mock_sender),
            logger=Mock(spec=Logger),
        )

    def test_ready_when_message_sent(self):
        self.mock_sender.send_message.return_value = True

        result = self.checker.check()

        assert result.ready is True
        assert result.message == "[READY] Telegram notifications"

    def test_not_ready_when_message_fails(self):
        self.mock_sender.send_message.return_value = False

        result = self.checker.check()

        assert result.ready is False
        assert result.message == "[NOT READY] Telegram notifications"

    def test_not_ready_when_unexpected_exception(self):
        self.mock_sender.send_message.side_effect = Exception("Connection error")

        result = self.checker.check()

        assert result.ready is False
        assert result.message == "[NOT READY] Telegram notifications"
