from unittest.mock import patch

from pryces.presentation.console.commands.base import CommandMetadata
from pryces.presentation.console.commands.list_monitors import ListMonitorsCommand


class TestListMonitorsCommand:

    def setup_method(self):
        self.command = ListMonitorsCommand()

    def test_get_metadata_returns_correct_metadata(self):
        metadata = self.command.get_metadata()

        assert isinstance(metadata, CommandMetadata)
        assert metadata.id == "list_monitors"
        assert metadata.name == "List Monitor Processes"

    def test_get_input_prompts_returns_empty_list(self):
        prompts = self.command.get_input_prompts()

        assert prompts == []

    @patch("pryces.presentation.console.commands.list_monitors.get_running_monitors")
    def test_execute_returns_no_processes_message_when_none_found(self, mock_get):
        mock_get.return_value = []

        result = self.command.execute()

        assert result == "No monitor processes found."

    @patch("pryces.presentation.console.commands.list_monitors.get_running_monitors")
    def test_execute_returns_single_process(self, mock_get):
        mock_get.return_value = [("12345", "/path/to/config.json")]

        result = self.command.execute()

        assert "Found 1 monitor process(es):" in result
        assert "1. PID 12345" in result
        assert "/path/to/config.json" in result

    @patch("pryces.presentation.console.commands.list_monitors.get_running_monitors")
    def test_execute_returns_multiple_processes(self, mock_get):
        mock_get.return_value = [("11111", "/config/a.json"), ("22222", "/config/b.json")]

        result = self.command.execute()

        assert "Found 2 monitor process(es):" in result
        assert "1. PID 11111" in result
        assert "/config/a.json" in result
        assert "2. PID 22222" in result
        assert "/config/b.json" in result
