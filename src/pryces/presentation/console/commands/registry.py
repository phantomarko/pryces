"""Command registry for managing available console commands."""

from typing import Dict
from .base import Command


class CommandRegistry:
    """Registry of available console commands."""

    def __init__(self) -> None:
        self._commands: Dict[str, Command] = {}

    def register(self, command: Command) -> None:
        """Register a command in the registry."""
        metadata = command.get_metadata()
        self._commands[metadata.id] = command

    def get_command(self, command_id: str) -> Command | None:
        """Retrieve a command by its ID."""
        return self._commands.get(command_id)

    def get_all_commands(self) -> list[Command]:
        """Get all registered commands."""
        return list(self._commands.values())
