import pytest
from unittest.mock import Mock

from pryces.presentation.console.commands.registry import CommandRegistry
from pryces.presentation.console.commands.base import Command, CommandMetadata


class TestCommandRegistry:

    def setup_method(self):
        self.registry = CommandRegistry()

    def test_register_command_adds_to_registry(self):
        mock_command = Mock(spec=Command)
        mock_command.get_metadata.return_value = CommandMetadata(
            id="test_cmd", name="Test Command", description="A test command"
        )

        self.registry.register(mock_command)

        retrieved = self.registry.get_command("test_cmd")
        assert retrieved is mock_command

    def test_get_command_returns_registered_command(self):
        mock_command1 = Mock(spec=Command)
        mock_command1.get_metadata.return_value = CommandMetadata(
            id="cmd1", name="Command 1", description="First command"
        )

        mock_command2 = Mock(spec=Command)
        mock_command2.get_metadata.return_value = CommandMetadata(
            id="cmd2", name="Command 2", description="Second command"
        )

        self.registry.register(mock_command1)
        self.registry.register(mock_command2)

        assert self.registry.get_command("cmd1") is mock_command1
        assert self.registry.get_command("cmd2") is mock_command2

    def test_get_command_returns_none_for_unknown_id(self):
        result = self.registry.get_command("nonexistent")
        assert result is None

    def test_get_all_commands_returns_all_registered(self):
        mock_command1 = Mock(spec=Command)
        mock_command1.get_metadata.return_value = CommandMetadata(
            id="cmd1", name="Command 1", description="First command"
        )

        mock_command2 = Mock(spec=Command)
        mock_command2.get_metadata.return_value = CommandMetadata(
            id="cmd2", name="Command 2", description="Second command"
        )

        self.registry.register(mock_command1)
        self.registry.register(mock_command2)

        all_commands = self.registry.get_all_commands()

        assert len(all_commands) == 2
        assert mock_command1 in all_commands
        assert mock_command2 in all_commands

    def test_get_all_commands_returns_empty_list_when_no_commands(self):
        all_commands = self.registry.get_all_commands()
        assert all_commands == []

    def test_register_overwrites_existing_command_with_same_id(self):
        mock_command1 = Mock(spec=Command)
        mock_command1.get_metadata.return_value = CommandMetadata(
            id="cmd", name="Command 1", description="First command"
        )

        mock_command2 = Mock(spec=Command)
        mock_command2.get_metadata.return_value = CommandMetadata(
            id="cmd", name="Command 2", description="Second command"
        )

        self.registry.register(mock_command1)
        self.registry.register(mock_command2)

        retrieved = self.registry.get_command("cmd")
        assert retrieved is mock_command2
        assert len(self.registry.get_all_commands()) == 1
