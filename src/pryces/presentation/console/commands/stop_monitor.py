import subprocess

from .base import Command, CommandMetadata, CommandResult, InputPrompt
from ..utils import (
    create_monitor_selection_validator,
    format_running_monitors,
    get_running_monitors,
)


class StopMonitorCommand(Command):
    def __init__(self) -> None:
        self._processes: list[tuple[str, str]] = []

    def get_metadata(self) -> CommandMetadata:
        return CommandMetadata(
            id="stop_monitor",
            name="Stop Monitor Process",
            description="Stop a running monitor process",
            show_progress=False,
        )

    def get_input_prompts(self) -> list[InputPrompt]:
        self._processes = get_running_monitors()

        if not self._processes:
            return []

        preamble = format_running_monitors(self._processes)
        count = len(self._processes)

        return [
            InputPrompt(
                key="selection",
                prompt=f"Enter number to stop (1-{count}, 0 to cancel): ",
                validator=create_monitor_selection_validator(count),
                preamble=preamble,
            )
        ]

    def execute(self, **kwargs) -> CommandResult:
        if not self._processes:
            return CommandResult(message="No monitor processes found.")

        selection = kwargs.get("selection")
        choice = int(selection)

        if choice == 0:
            return CommandResult(message="Cancelled.")

        pid, config_path = self._processes[choice - 1]
        subprocess.run(["kill", pid])
        return CommandResult(message=f"Stopped monitor process PID {pid} (config: {config_path}).")
