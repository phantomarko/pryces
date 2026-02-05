from typing import Dict
from .base import Command


class CommandRegistry:
    def __init__(self) -> None:
        self._commands: Dict[str, Command] = {}

    def register(self, command: Command) -> None:
        metadata = command.get_metadata()
        self._commands[metadata.id] = command

    def get_command(self, command_id: str) -> Command | None:
        return self._commands.get(command_id)

    def get_all_commands(self) -> list[Command]:
        return list(self._commands.values())
