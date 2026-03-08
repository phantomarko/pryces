from unittest.mock import patch

from pryces.presentation.console.commands.base import CommandMetadata
from pryces.presentation.console.commands.stop_monitor import StopMonitorCommand


class TestStopMonitorCommand:

    def test_get_metadata_returns_correct_metadata(self):
        command = StopMonitorCommand()
        metadata = command.get_metadata()

        assert isinstance(metadata, CommandMetadata)
        assert metadata.id == "stop_monitor"
        assert metadata.name == "Stop Monitor Process"

    @patch("pryces.presentation.console.commands.stop_monitor.get_running_monitors")
    def test_get_input_prompts_returns_empty_list_when_no_processes(self, mock_get):
        mock_get.return_value = []
        command = StopMonitorCommand()

        prompts = command.get_input_prompts()

        assert prompts == []

    @patch("pryces.presentation.console.commands.stop_monitor.get_running_monitors")
    def test_get_input_prompts_returns_prompt_with_preamble(self, mock_get):
        mock_get.return_value = [("11111", "/config/a.json"), ("22222", "/config/b.json")]
        command = StopMonitorCommand()

        prompts = command.get_input_prompts()

        assert len(prompts) == 1
        prompt = prompts[0]
        assert prompt.key == "selection"
        assert "1-2" in prompt.prompt
        assert "0 to cancel" in prompt.prompt
        assert "Found 2 monitor process(es):" in prompt.preamble
        assert "PID 11111" in prompt.preamble
        assert "/config/a.json" in prompt.preamble
        assert "PID 22222" in prompt.preamble
        assert "/config/b.json" in prompt.preamble

    @patch("pryces.presentation.console.commands.stop_monitor.get_running_monitors")
    def test_get_input_prompts_validator_accepts_valid_range(self, mock_get):
        mock_get.return_value = [("11111", "/config/a.json"), ("22222", "/config/b.json")]
        command = StopMonitorCommand()

        prompts = command.get_input_prompts()
        validator = prompts[0].validator

        assert validator("0") is True
        assert validator("1") is True
        assert validator("2") is True
        assert validator("3") is False
        assert validator("abc") is False

    @patch("pryces.presentation.console.commands.stop_monitor.get_running_monitors")
    def test_execute_returns_no_processes_message_when_no_processes(self, mock_get):
        mock_get.return_value = []
        command = StopMonitorCommand()
        command.get_input_prompts()

        result = command.execute()

        assert result.message == "No monitor processes found."

    @patch("pryces.presentation.console.commands.stop_monitor.get_running_monitors")
    def test_execute_returns_cancelled_on_zero(self, mock_get):
        mock_get.return_value = [("12345", "/config/a.json")]
        command = StopMonitorCommand()
        command.get_input_prompts()

        result = command.execute(selection="0")

        assert result.message == "Cancelled."

    @patch("pryces.presentation.console.commands.stop_monitor.subprocess.run")
    @patch("pryces.presentation.console.commands.stop_monitor.get_running_monitors")
    def test_execute_kills_selected_process(self, mock_get, mock_run):
        mock_get.return_value = [("11111", "/config/a.json"), ("22222", "/config/b.json")]
        command = StopMonitorCommand()
        command.get_input_prompts()

        result = command.execute(selection="2")

        mock_run.assert_called_once_with(["kill", "22222"])
        assert "22222" in result.message
        assert "/config/b.json" in result.message
