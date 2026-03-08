import subprocess
import sys
from io import TextIOBase

from .base import Command, CommandMetadata, CommandResult, InputPrompt
from ..utils import format_running_monitors, get_running_monitors


class StopMonitorCommand(Command):
    def __init__(
        self,
        input_stream: TextIOBase = sys.stdin,
        output_stream: TextIOBase = sys.stdout,
    ) -> None:
        self._input_stream = input_stream
        self._output_stream = output_stream

    def get_metadata(self) -> CommandMetadata:
        return CommandMetadata(
            id="stop_monitor",
            name="Stop Monitor Process",
            description="Stop a running monitor process",
        )

    def get_input_prompts(self) -> list[InputPrompt]:
        return []

    def execute(self, **kwargs) -> CommandResult:
        processes = get_running_monitors()

        if not processes:
            return CommandResult(message="No monitor processes found.")

        self._output_stream.write(format_running_monitors(processes) + "\n")
        self._output_stream.flush()

        while True:
            self._output_stream.write(f"\nEnter number to stop (1-{len(processes)}, 0 to cancel): ")
            self._output_stream.flush()
            raw = self._input_stream.readline().strip()

            if not raw.isdigit():
                self._output_stream.write("Invalid input. Please enter a number.\n")
                self._output_stream.flush()
                continue

            choice = int(raw)

            if choice == 0:
                return CommandResult(message="Cancelled.")

            if 1 <= choice <= len(processes):
                pid, config_path = processes[choice - 1]
                subprocess.run(["kill", pid])
                return CommandResult(
                    message=f"Stopped monitor process PID {pid} (config: {config_path})."
                )

            self._output_stream.write(
                f"Invalid choice. Enter a number between 0 and {len(processes)}.\n"
            )
            self._output_stream.flush()
