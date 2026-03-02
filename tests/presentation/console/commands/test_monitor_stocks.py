import subprocess
import sys
from unittest.mock import Mock, patch

from pryces.presentation.console.commands.base import CommandMetadata, InputPrompt
from pryces.presentation.console.commands.monitor_stocks import MonitorStocksCommand
from pryces.presentation.console.utils import validate_file_path, validate_non_negative_integer


class TestMonitorStocksCommand:

    def setup_method(self):
        self.command = MonitorStocksCommand()

    def test_get_metadata_returns_correct_metadata(self):
        metadata = self.command.get_metadata()

        assert isinstance(metadata, CommandMetadata)
        assert metadata.id == "monitor_stocks"
        assert metadata.name == "Monitor Stocks"

    def test_get_input_prompts_returns_config_path_prompt(self):
        prompts = self.command.get_input_prompts()

        assert len(prompts) == 2
        assert isinstance(prompts[0], InputPrompt)
        assert prompts[0].key == "config_path"
        assert "json" in prompts[0].prompt.lower()
        assert prompts[0].validator is validate_file_path

    def test_get_input_prompts_returns_extra_delay_prompt(self):
        prompts = self.command.get_input_prompts()

        assert isinstance(prompts[1], InputPrompt)
        assert prompts[1].key == "extra_delay"
        assert "delay" in prompts[1].prompt.lower()
        assert prompts[1].validator is validate_non_negative_integer

    @patch("pryces.presentation.console.commands.monitor_stocks.subprocess.Popen")
    def test_execute_launches_background_process_and_returns_pid(self, mock_popen):
        mock_process = Mock()
        mock_process.pid = 12345
        mock_popen.return_value = mock_process

        result = self.command.execute(config_path="/path/to/config.json")

        mock_popen.assert_called_once_with(
            [
                sys.executable,
                "-m",
                "pryces.presentation.scripts.monitor_stocks",
                "/path/to/config.json",
                "--extra-delay",
                "0",
            ],
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        assert "PID: 12345" in result.message

    @patch("pryces.presentation.console.commands.monitor_stocks.subprocess.Popen")
    def test_execute_strips_whitespace_from_config_path(self, mock_popen):
        mock_process = Mock()
        mock_process.pid = 99999
        mock_popen.return_value = mock_process

        result = self.command.execute(config_path="  /path/to/config.json  ")

        args = mock_popen.call_args[0][0]
        assert args[3] == "/path/to/config.json"
        assert "PID: 99999" in result.message

    @patch("pryces.presentation.console.commands.monitor_stocks.subprocess.Popen")
    def test_execute_accepts_kwargs_for_compatibility(self, mock_popen):
        mock_process = Mock()
        mock_process.pid = 1
        mock_popen.return_value = mock_process

        result = self.command.execute(config_path="/path/to/config.json", extra_arg="ignored")

        assert "Monitor started in background" in result.message

    @patch("pryces.presentation.console.commands.monitor_stocks.subprocess.Popen")
    def test_execute_returns_message_with_background_info(self, mock_popen):
        mock_process = Mock()
        mock_process.pid = 42
        mock_popen.return_value = mock_process

        result = self.command.execute(config_path="/path/to/config.json")

        assert result.message == "Monitor started in background (PID: 42)"

    @patch("pryces.presentation.console.commands.monitor_stocks.subprocess.Popen")
    def test_execute_passes_extra_delay_to_subprocess(self, mock_popen):
        mock_process = Mock()
        mock_process.pid = 100
        mock_popen.return_value = mock_process

        self.command.execute(config_path="/path/to/config.json", extra_delay="5")

        args = mock_popen.call_args[0][0]
        assert "--extra-delay" in args
        assert args[args.index("--extra-delay") + 1] == "5"

    @patch("pryces.presentation.console.commands.monitor_stocks.subprocess.Popen")
    def test_execute_defaults_extra_delay_to_zero_when_empty(self, mock_popen):
        mock_process = Mock()
        mock_process.pid = 100
        mock_popen.return_value = mock_process

        self.command.execute(config_path="/path/to/config.json", extra_delay="")

        args = mock_popen.call_args[0][0]
        assert "--extra-delay" in args
        assert args[args.index("--extra-delay") + 1] == "0"

    @patch("pryces.presentation.console.commands.monitor_stocks.subprocess.Popen")
    def test_execute_defaults_extra_delay_to_zero_when_not_provided(self, mock_popen):
        mock_process = Mock()
        mock_process.pid = 100
        mock_popen.return_value = mock_process

        self.command.execute(config_path="/path/to/config.json")

        args = mock_popen.call_args[0][0]
        assert "--extra-delay" in args
        assert args[args.index("--extra-delay") + 1] == "0"
