"""Unit tests for InteractiveMenu."""

from io import StringIO
from unittest.mock import Mock

import pytest

from pryces.presentation.console.menu import InteractiveMenu
from pryces.presentation.console.commands.base import Command, CommandMetadata, InputPrompt
from pryces.presentation.console.commands.registry import CommandRegistry


class TestInteractiveMenu:
    """Test suite for InteractiveMenu."""

    def setup_method(self):
        """Set up test fixtures."""
        self.registry = CommandRegistry()
        self.input_stream = StringIO()
        self.output_stream = StringIO()
        self.menu = InteractiveMenu(
            registry=self.registry,
            input_stream=self.input_stream,
            output_stream=self.output_stream
        )

    def test_display_menu_shows_all_commands(self):
        """Test that display_menu shows all registered commands."""
        mock_command1 = Mock(spec=Command)
        mock_command1.get_metadata.return_value = CommandMetadata(
            id="cmd1",
            name="Command One",
            description="First test command"
        )

        mock_command2 = Mock(spec=Command)
        mock_command2.get_metadata.return_value = CommandMetadata(
            id="cmd2",
            name="Command Two",
            description="Second test command"
        )

        self.registry.register(mock_command1)
        self.registry.register(mock_command2)

        self.menu._display_menu()

        output = self.output_stream.getvalue()
        assert "PRYCES" in output
        assert "Command One" in output
        assert "First test command" in output
        assert "Command Two" in output
        assert "Second test command" in output
        assert "0. Exit" in output

    def test_get_selection_returns_valid_number(self):
        """Test that get_selection returns valid numeric input."""
        self.input_stream.write("1\n")
        self.input_stream.seek(0)

        selection = self.menu._get_selection()

        assert selection == 1

    def test_get_selection_handles_invalid_input(self):
        """Test that get_selection handles non-numeric input."""
        self.input_stream.write("abc\n2\n")
        self.input_stream.seek(0)

        selection = self.menu._get_selection()

        assert selection == 2
        output = self.output_stream.getvalue()
        assert "Invalid input" in output

    def test_get_selection_handles_empty_input(self):
        """Test that get_selection re-prompts on empty input."""
        self.input_stream.write("\n\n3\n")
        self.input_stream.seek(0)

        selection = self.menu._get_selection()

        assert selection == 3

    def test_get_selection_returns_zero_on_eof(self):
        """Test that get_selection returns 0 on EOF."""
        selection = self.menu._get_selection()

        assert selection == 0

    def test_collect_inputs_gathers_all_prompts(self):
        """Test that collect_inputs gathers input for all prompts."""
        prompts = [
            InputPrompt(key="name", prompt="Enter name: ", validator=None),
            InputPrompt(key="age", prompt="Enter age: ", validator=None)
        ]

        self.input_stream.write("John\n25\n")
        self.input_stream.seek(0)

        inputs = self.menu._collect_inputs(prompts)

        assert inputs == {"name": "John", "age": "25"}

    def test_collect_inputs_validates_input(self):
        """Test that collect_inputs validates input using validator."""
        def validate_number(value: str) -> bool:
            return value.isdigit()

        prompts = [
            InputPrompt(key="count", prompt="Enter count: ", validator=validate_number)
        ]

        self.input_stream.write("abc\nxyz\n42\n")
        self.input_stream.seek(0)

        inputs = self.menu._collect_inputs(prompts)

        assert inputs == {"count": "42"}
        output = self.output_stream.getvalue()
        assert output.count("Invalid input format") == 2

    def test_collect_inputs_rejects_empty_input(self):
        """Test that collect_inputs rejects empty input."""
        prompts = [
            InputPrompt(key="value", prompt="Enter value: ", validator=None)
        ]

        self.input_stream.write("\n\ntest\n")
        self.input_stream.seek(0)

        inputs = self.menu._collect_inputs(prompts)

        assert inputs == {"value": "test"}
        output = self.output_stream.getvalue()
        assert "cannot be empty" in output

    def test_collect_inputs_returns_none_on_eof(self):
        """Test that collect_inputs returns None on EOF."""
        prompts = [
            InputPrompt(key="value", prompt="Enter value: ", validator=None)
        ]

        inputs = self.menu._collect_inputs(prompts)

        assert inputs is None

    def test_execute_command_collects_inputs_and_executes(self):
        """Test that execute_command collects inputs and executes command."""
        mock_command = Mock(spec=Command)
        mock_command.get_metadata.return_value = CommandMetadata(
            id="test",
            name="Test Command",
            description="Test"
        )
        mock_command.get_input_prompts.return_value = [
            InputPrompt(key="symbol", prompt="Enter symbol: ", validator=None)
        ]
        mock_command.execute.return_value = '{"success": true}'

        self.input_stream.write("AAPL\n")
        self.input_stream.seek(0)

        self.menu._execute_command(mock_command)

        mock_command.execute.assert_called_once_with(symbol="AAPL")
        output = self.output_stream.getvalue()
        assert "Test Command" in output
        assert '{"success": true}' in output

    def test_execute_command_handles_exception(self):
        """Test that execute_command handles exceptions gracefully."""
        mock_command = Mock(spec=Command)
        mock_command.get_metadata.return_value = CommandMetadata(
            id="test",
            name="Test Command",
            description="Test"
        )
        mock_command.get_input_prompts.return_value = []
        mock_command.execute.side_effect = Exception("Test error")

        self.menu._execute_command(mock_command)

        output = self.output_stream.getvalue()
        assert "Error executing command" in output
        assert "Test error" in output

    def test_execute_command_handles_cancelled_input(self):
        """Test that execute_command handles cancelled input collection."""
        mock_command = Mock(spec=Command)
        mock_command.get_metadata.return_value = CommandMetadata(
            id="test",
            name="Test Command",
            description="Test"
        )
        mock_command.get_input_prompts.return_value = [
            InputPrompt(key="value", prompt="Enter value: ", validator=None)
        ]

        self.menu._execute_command(mock_command)

        mock_command.execute.assert_not_called()
        output = self.output_stream.getvalue()
        assert "cancelled" in output

    def test_execute_command_prompts_to_continue(self):
        """Test that execute_command shows press enter prompt after execution."""
        mock_command = Mock(spec=Command)
        mock_command.get_metadata.return_value = CommandMetadata(
            id="test",
            name="Test Command",
            description="Test"
        )
        mock_command.get_input_prompts.return_value = []
        mock_command.execute.return_value = '{"success": true}'

        self.input_stream.write("\n")
        self.input_stream.seek(0)

        self.menu._execute_command(mock_command)

        output = self.output_stream.getvalue()
        assert "Press Enter to continue" in output

    def test_run_loops_until_exit_selected(self):
        """Test that run loops through menu until exit is selected."""
        mock_command = Mock(spec=Command)
        mock_command.get_metadata.return_value = CommandMetadata(
            id="test",
            name="Test Command",
            description="Test"
        )
        mock_command.get_input_prompts.return_value = []
        mock_command.execute.return_value = '{"success": true}'

        self.registry.register(mock_command)

        self.input_stream.write("1\n\n1\n\n0\n")
        self.input_stream.seek(0)

        self.menu.run()

        assert mock_command.execute.call_count == 2
        output = self.output_stream.getvalue()
        assert "Goodbye" in output

    def test_run_handles_invalid_selection(self):
        """Test that run handles invalid menu selections."""
        mock_command = Mock(spec=Command)
        mock_command.get_metadata.return_value = CommandMetadata(
            id="test",
            name="Test Command",
            description="Test"
        )

        self.registry.register(mock_command)

        self.input_stream.write("99\n0\n")
        self.input_stream.seek(0)

        self.menu.run()

        output = self.output_stream.getvalue()
        assert "Invalid selection: 99" in output

    def test_run_handles_eof_gracefully(self):
        """Test that run handles EOF (Ctrl+D) gracefully."""
        mock_command = Mock(spec=Command)
        mock_command.get_metadata.return_value = CommandMetadata(
            id="test",
            name="Test Command",
            description="Test"
        )

        self.registry.register(mock_command)

        self.menu.run()

        output = self.output_stream.getvalue()
        assert "Goodbye" in output
