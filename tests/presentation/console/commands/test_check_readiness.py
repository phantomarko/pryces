from unittest.mock import Mock, patch

from pryces.application.interfaces import MessageSender
from pryces.application.use_cases.send_messages import SendMessages
from pryces.presentation.console.commands.check_readiness import CheckReadinessCommand
from pryces.presentation.console.commands.base import CommandMetadata


class TestCheckReadinessCommand:

    def setup_method(self):
        self.mock_sender = Mock(spec=MessageSender)
        use_case = SendMessages(sender=self.mock_sender)
        self.command = CheckReadinessCommand(use_case)

    def test_get_metadata_returns_correct_metadata(self):
        metadata = self.command.get_metadata()

        assert isinstance(metadata, CommandMetadata)
        assert metadata.id == "check_readiness"
        assert metadata.name == "Check Readiness"
        assert (
            metadata.description == "Check if all components and configs are ready for monitoring"
        )

    def test_get_input_prompts_returns_empty_list(self):
        prompts = self.command.get_input_prompts()

        assert prompts == []

    def test_all_ready_is_true_by_default(self):
        assert self.command._all_ready is True


class TestCheckReadinessEnv:

    def setup_method(self):
        self.mock_sender = Mock(spec=MessageSender)
        use_case = SendMessages(sender=self.mock_sender)
        self.command = CheckReadinessCommand(use_case)

    @patch.dict(
        "os.environ",
        {
            "TELEGRAM_BOT_TOKEN": "token",
            "TELEGRAM_GROUP_ID": "123",
            "MAX_FETCH_WORKERS": "4",
        },
        clear=True,
    )
    def test_env_ready_when_all_required_vars_valid(self):
        result = self.command._check_env()

        assert result == "[READY] Environment variables"
        assert self.command._all_ready is True

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
    def test_env_ready_when_logs_directory_exists(self):
        result = self.command._check_env()

        assert result == "[READY] Environment variables"

    @patch.dict("os.environ", {"MAX_FETCH_WORKERS": "4"}, clear=True)
    def test_env_not_ready_when_telegram_vars_missing(self):
        result = self.command._check_env()

        assert "[NOT READY] Environment variables" in result
        assert "TELEGRAM_BOT_TOKEN is missing or empty" in result
        assert "TELEGRAM_GROUP_ID is missing or empty" in result
        assert self.command._all_ready is False

    @patch.dict(
        "os.environ",
        {
            "TELEGRAM_BOT_TOKEN": "  ",
            "TELEGRAM_GROUP_ID": "",
            "MAX_FETCH_WORKERS": "4",
        },
        clear=True,
    )
    def test_env_not_ready_when_telegram_vars_blank(self):
        result = self.command._check_env()

        assert "[NOT READY] Environment variables" in result
        assert "TELEGRAM_BOT_TOKEN is missing or empty" in result
        assert "TELEGRAM_GROUP_ID is missing or empty" in result

    @patch.dict(
        "os.environ",
        {
            "TELEGRAM_BOT_TOKEN": "token",
            "TELEGRAM_GROUP_ID": "123",
            "MAX_FETCH_WORKERS": "abc",
        },
        clear=True,
    )
    def test_env_not_ready_when_max_fetch_workers_not_integer(self):
        result = self.command._check_env()

        assert "[NOT READY] Environment variables" in result
        assert "MAX_FETCH_WORKERS is missing or not a valid integer" in result

    @patch.dict(
        "os.environ",
        {
            "TELEGRAM_BOT_TOKEN": "token",
            "TELEGRAM_GROUP_ID": "123",
        },
        clear=True,
    )
    def test_env_not_ready_when_max_fetch_workers_missing(self):
        result = self.command._check_env()

        assert "[NOT READY] Environment variables" in result
        assert "MAX_FETCH_WORKERS is missing or not a valid integer" in result

    @patch.dict(
        "os.environ",
        {
            "TELEGRAM_BOT_TOKEN": "token",
            "TELEGRAM_GROUP_ID": "123",
            "MAX_FETCH_WORKERS": "0",
        },
        clear=True,
    )
    def test_env_not_ready_when_max_fetch_workers_zero(self):
        result = self.command._check_env()

        assert "[NOT READY] Environment variables" in result
        assert "MAX_FETCH_WORKERS must be a positive integer" in result

    @patch.dict(
        "os.environ",
        {
            "TELEGRAM_BOT_TOKEN": "token",
            "TELEGRAM_GROUP_ID": "123",
            "MAX_FETCH_WORKERS": "-1",
        },
        clear=True,
    )
    def test_env_not_ready_when_max_fetch_workers_negative(self):
        result = self.command._check_env()

        assert "[NOT READY] Environment variables" in result
        assert "MAX_FETCH_WORKERS must be a positive integer" in result

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
    def test_env_not_ready_when_logs_directory_not_exists(self):
        result = self.command._check_env()

        assert "[NOT READY] Environment variables" in result
        assert "LOGS_DIRECTORY is not a valid directory" in result

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
    def test_env_ready_when_logs_directory_empty(self):
        result = self.command._check_env()

        assert result == "[READY] Environment variables"


class TestCheckReadinessTelegram:

    def setup_method(self):
        self.mock_sender = Mock(spec=MessageSender)
        use_case = SendMessages(sender=self.mock_sender)
        self.command = CheckReadinessCommand(use_case)

    def test_telegram_ready_when_notification_sent(self):
        self.mock_sender.send_message.return_value = True

        result = self.command._check_telegram()

        assert result == "[READY] Telegram notifications"
        assert self.command._all_ready is True

    def test_telegram_not_ready_when_notification_fails(self):
        self.mock_sender.send_message.return_value = False

        result = self.command._check_telegram()

        assert result == "[NOT READY] Telegram notifications"
        assert self.command._all_ready is False

    def test_telegram_not_ready_when_unexpected_exception(self):
        self.mock_sender.send_message.side_effect = Exception("Connection error")

        result = self.command._check_telegram()

        assert result == "[NOT READY] Telegram notifications"
        assert self.command._all_ready is False


class TestCheckReadinessExecute:

    @patch.dict(
        "os.environ",
        {
            "TELEGRAM_BOT_TOKEN": "token",
            "TELEGRAM_GROUP_ID": "123",
            "MAX_FETCH_WORKERS": "4",
        },
        clear=True,
    )
    def test_execute_does_not_include_warning_when_all_ready(self):
        mock_sender = Mock(spec=MessageSender)
        mock_sender.send_message.return_value = True
        use_case = SendMessages(sender=mock_sender)
        command = CheckReadinessCommand(use_case)

        result = command.execute()

        lines = result.split("\n")
        assert lines[0] == "[READY] Environment variables"
        assert lines[1] == "[READY] Telegram notifications"
        assert "restart the app" not in result

    @patch.dict(
        "os.environ",
        {
            "MAX_FETCH_WORKERS": "4",
        },
        clear=True,
    )
    def test_execute_includes_warning_when_any_check_fails(self):
        mock_sender = Mock(spec=MessageSender)
        mock_sender.send_message.return_value = False
        use_case = SendMessages(sender=mock_sender)
        command = CheckReadinessCommand(use_case)

        result = command.execute()

        assert result.index("[NOT READY] Environment variables") < result.index(
            "[NOT READY] Telegram notifications"
        )
        assert result.endswith(
            "Fix the errors above and restart the app for changes to take effect."
        )
