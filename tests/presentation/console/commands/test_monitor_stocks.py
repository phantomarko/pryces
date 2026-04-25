import subprocess
import sys
from unittest.mock import Mock, patch

import pytest

from pryces.infrastructure.configs import ConfigStore
from pryces.presentation.console.commands.base import CommandMetadata
from pryces.presentation.console.commands.monitor_stocks import MonitorStocksCommand
from pryces.presentation.console.utils import (
    validate_non_negative_integer,
    validate_positive_integer,
)


class TestMonitorStocksCommand:

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        self.tmp_path = tmp_path
        self.command = MonitorStocksCommand(ConfigStore(tmp_path))

    def test_get_metadata_returns_correct_metadata(self):
        metadata = self.command.get_metadata()

        assert isinstance(metadata, CommandMetadata)
        assert metadata.id == "monitor_stocks"
        assert metadata.name == "Execute Monitor Process"
        assert metadata.show_progress is False

    def test_get_input_prompts_returns_empty_when_no_configs(self):
        assert self.command.get_input_prompts() == []

    def test_get_input_prompts_returns_three_prompts_when_configs_exist(self):
        (self.tmp_path / "portfolio.json").touch()

        prompts = self.command.get_input_prompts()

        assert len(prompts) == 3
        assert prompts[0].key == "config_selection"
        assert prompts[1].key == "duration"
        assert prompts[1].validator is validate_positive_integer
        assert prompts[2].key == "extra_delay"
        assert prompts[2].validator is validate_non_negative_integer
        assert prompts[2].default == "0"

    def test_execute_returns_error_when_no_configs(self):
        self.command.get_input_prompts()
        result = self.command.execute()
        assert result.success is False
        assert "No configs" in result.message

    @patch("pryces.presentation.console.commands.monitor_stocks.subprocess.Popen")
    def test_execute_launches_background_process_and_returns_pid(self, mock_popen):
        path = self.tmp_path / "portfolio.json"
        path.touch()
        self.command.get_input_prompts()

        mock_process = Mock()
        mock_process.pid = 12345
        mock_popen.return_value = mock_process

        result = self.command.execute(config_selection="1", duration="10")

        mock_popen.assert_called_once_with(
            [
                sys.executable,
                "-m",
                "pryces.presentation.scripts.monitor_stocks",
                str(path),
                "--duration",
                "10",
                "--extra-delay",
                "0",
            ],
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        assert "PID: 12345" in result.message

    @patch("pryces.presentation.console.commands.monitor_stocks.subprocess.Popen")
    def test_execute_passes_extra_delay_to_subprocess(self, mock_popen):
        path = self.tmp_path / "portfolio.json"
        path.touch()
        self.command.get_input_prompts()

        mock_process = Mock()
        mock_process.pid = 100
        mock_popen.return_value = mock_process

        self.command.execute(config_selection="1", duration="10", extra_delay="5")

        args = mock_popen.call_args[0][0]
        assert "--extra-delay" in args
        assert args[args.index("--extra-delay") + 1] == "5"

    @patch("pryces.presentation.console.commands.monitor_stocks.subprocess.Popen")
    def test_execute_defaults_extra_delay_to_zero_when_empty(self, mock_popen):
        path = self.tmp_path / "portfolio.json"
        path.touch()
        self.command.get_input_prompts()

        mock_process = Mock()
        mock_process.pid = 100
        mock_popen.return_value = mock_process

        self.command.execute(config_selection="1", duration="10", extra_delay="")

        args = mock_popen.call_args[0][0]
        assert args[args.index("--extra-delay") + 1] == "0"

    @patch("pryces.presentation.console.commands.monitor_stocks.subprocess.Popen")
    def test_execute_returns_message_with_background_info(self, mock_popen):
        path = self.tmp_path / "portfolio.json"
        path.touch()
        self.command.get_input_prompts()

        mock_process = Mock()
        mock_process.pid = 42
        mock_popen.return_value = mock_process

        result = self.command.execute(config_selection="1", duration="10")

        assert result.message == "Monitor started in background (PID: 42)"

    @patch("pryces.presentation.console.commands.monitor_stocks.subprocess.Popen")
    def test_execute_returns_failure_when_popen_raises(self, mock_popen):
        path = self.tmp_path / "portfolio.json"
        path.touch()
        self.command.get_input_prompts()
        mock_popen.side_effect = OSError("executable not found")

        result = self.command.execute(config_selection="1", duration="10")

        assert result.success is False
        assert "executable not found" in result.message
        assert "Failed to start monitor process" in result.message

    @patch("pryces.presentation.console.commands.monitor_stocks.subprocess.Popen")
    def test_execute_passes_duration_to_subprocess(self, mock_popen):
        path = self.tmp_path / "portfolio.json"
        path.touch()
        self.command.get_input_prompts()

        mock_process = Mock()
        mock_process.pid = 100
        mock_popen.return_value = mock_process

        self.command.execute(config_selection="1", duration="30")

        args = mock_popen.call_args[0][0]
        assert "--duration" in args
        assert args[args.index("--duration") + 1] == "30"
