from io import StringIO
from unittest.mock import patch, Mock

from pryces.presentation.console.commands.base import CommandMetadata
from pryces.presentation.console.commands.stop_monitor import StopMonitorCommand


def _make_command(input_text: str = "") -> tuple[StopMonitorCommand, StringIO]:
    output_stream = StringIO()
    input_stream = StringIO(input_text)
    command = StopMonitorCommand(input_stream=input_stream, output_stream=output_stream)
    return command, output_stream


class TestStopMonitorCommand:

    def test_get_metadata_returns_correct_metadata(self):
        command, _ = _make_command()
        metadata = command.get_metadata()

        assert isinstance(metadata, CommandMetadata)
        assert metadata.id == "stop_monitor"
        assert metadata.name == "Stop Monitor Process"

    def test_get_input_prompts_returns_empty_list(self):
        command, _ = _make_command()

        assert command.get_input_prompts() == []

    @patch("pryces.presentation.console.commands.stop_monitor._get_monitor_processes")
    def test_execute_returns_early_when_no_processes(self, mock_get):
        mock_get.return_value = []
        command, _ = _make_command()

        result = command.execute()

        assert result == "No monitor processes found."

    @patch("pryces.presentation.console.commands.stop_monitor._get_monitor_processes")
    def test_execute_prints_numbered_list(self, mock_get):
        mock_get.return_value = [("11111", "/config/a.json"), ("22222", "/config/b.json")]
        command, output_stream = _make_command("0\n")

        command.execute()

        output = output_stream.getvalue()
        assert "Found 2 monitor process(es):" in output
        assert "1. PID 11111" in output
        assert "/config/a.json" in output
        assert "2. PID 22222" in output
        assert "/config/b.json" in output

    @patch("pryces.presentation.console.commands.stop_monitor._get_monitor_processes")
    def test_execute_returns_cancelled_on_zero(self, mock_get):
        mock_get.return_value = [("12345", "/config/a.json")]
        command, _ = _make_command("0\n")

        result = command.execute()

        assert result == "Cancelled."

    @patch("pryces.presentation.console.commands.stop_monitor.subprocess.run")
    @patch("pryces.presentation.console.commands.stop_monitor._get_monitor_processes")
    def test_execute_kills_selected_process(self, mock_get, mock_run):
        mock_get.return_value = [("11111", "/config/a.json"), ("22222", "/config/b.json")]
        command, _ = _make_command("2\n")

        result = command.execute()

        mock_run.assert_called_once_with(["kill", "22222"])
        assert "22222" in result
        assert "/config/b.json" in result

    @patch("pryces.presentation.console.commands.stop_monitor.subprocess.run")
    @patch("pryces.presentation.console.commands.stop_monitor._get_monitor_processes")
    def test_execute_rejects_out_of_range_then_accepts_valid(self, mock_get, mock_run):
        mock_get.return_value = [("12345", "/config/a.json")]
        command, output_stream = _make_command("5\n1\n")

        result = command.execute()

        output = output_stream.getvalue()
        assert "Invalid choice" in output
        mock_run.assert_called_once_with(["kill", "12345"])
        assert "12345" in result

    @patch("pryces.presentation.console.commands.stop_monitor.subprocess.run")
    @patch("pryces.presentation.console.commands.stop_monitor._get_monitor_processes")
    def test_execute_rejects_non_numeric_then_accepts_valid(self, mock_get, mock_run):
        mock_get.return_value = [("12345", "/config/a.json")]
        command, output_stream = _make_command("abc\n1\n")

        result = command.execute()

        output = output_stream.getvalue()
        assert "Invalid input" in output
        mock_run.assert_called_once_with(["kill", "12345"])
        assert "12345" in result
