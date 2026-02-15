from unittest.mock import patch, Mock

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

    @patch("pryces.presentation.console.commands.list_monitors.subprocess.run")
    def test_execute_returns_no_processes_message_when_none_found(self, mock_run):
        mock_run.return_value = Mock(
            stdout="USER       PID  %CPU %MEM    VSZ   RSS TTY STAT START TIME COMMAND\nroot         1  0.0  0.0   1234   567 ?   Ss   00:00 0:00 /sbin/init\n"
        )

        result = self.command.execute()

        assert result == "No monitor processes found."

    @patch("pryces.presentation.console.commands.list_monitors.subprocess.run")
    def test_execute_returns_single_process(self, mock_run):
        mock_run.return_value = Mock(
            stdout=(
                "USER       PID  %CPU %MEM    VSZ   RSS TTY STAT START TIME COMMAND\n"
                "user     12345  0.5  1.0  54321  9876 ?   S    10:00 0:01 /usr/bin/python -m pryces.presentation.scripts.monitor_stocks /path/to/config.json\n"
            )
        )

        result = self.command.execute()

        assert "Found 1 monitor process(es):" in result
        assert "PID 12345" in result
        assert "/path/to/config.json" in result

    @patch("pryces.presentation.console.commands.list_monitors.subprocess.run")
    def test_execute_returns_multiple_processes(self, mock_run):
        mock_run.return_value = Mock(
            stdout=(
                "USER       PID  %CPU %MEM    VSZ   RSS TTY STAT START TIME COMMAND\n"
                "user     11111  0.5  1.0  54321  9876 ?   S    10:00 0:01 /usr/bin/python -m pryces.presentation.scripts.monitor_stocks /config/a.json\n"
                "user     22222  0.3  0.8  43210  8765 ?   S    10:05 0:00 /usr/bin/python -m pryces.presentation.scripts.monitor_stocks /config/b.json\n"
            )
        )

        result = self.command.execute()

        assert "Found 2 monitor process(es):" in result
        assert "PID 11111" in result
        assert "/config/a.json" in result
        assert "PID 22222" in result
        assert "/config/b.json" in result

    @patch("pryces.presentation.console.commands.list_monitors.subprocess.run")
    def test_execute_excludes_ps_aux_own_line(self, mock_run):
        mock_run.return_value = Mock(
            stdout=(
                "USER       PID  %CPU %MEM    VSZ   RSS TTY STAT START TIME COMMAND\n"
                "user     12345  0.5  1.0  54321  9876 ?   S    10:00 0:01 /usr/bin/python -m pryces.presentation.scripts.monitor_stocks /path/to/config.json\n"
                "user     99999  0.0  0.0  12345  1234 ?   S    10:01 0:00 ps aux\n"
            )
        )

        result = self.command.execute()

        assert "Found 1 monitor process(es):" in result
        assert "PID 12345" in result
        assert "99999" not in result

    @patch("pryces.presentation.console.commands.list_monitors.subprocess.run")
    def test_execute_shows_unknown_config_when_no_args_after_module(self, mock_run):
        mock_run.return_value = Mock(
            stdout=(
                "USER       PID  %CPU %MEM    VSZ   RSS TTY STAT START TIME COMMAND\n"
                "user     12345  0.5  1.0  54321  9876 ?   S    10:00 0:01 /usr/bin/python -m pryces.presentation.scripts.monitor_stocks\n"
            )
        )

        result = self.command.execute()

        assert "PID 12345" in result
        assert "unknown" in result

    @patch("pryces.presentation.console.commands.list_monitors.subprocess.run")
    def test_execute_calls_ps_aux_with_capture(self, mock_run):
        mock_run.return_value = Mock(stdout="")

        self.command.execute()

        mock_run.assert_called_once_with(["ps", "aux"], capture_output=True, text=True)
