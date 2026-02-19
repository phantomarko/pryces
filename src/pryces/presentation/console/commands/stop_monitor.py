import subprocess
import sys
from io import TextIOBase

from .base import Command, CommandMetadata, InputPrompt
from .list_monitors import _get_monitor_processes


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

    def execute(self, **kwargs) -> str:
        processes = _get_monitor_processes()

        if not processes:
            return "No monitor processes found."

        header = f"Found {len(processes)} monitor process(es):"
        entries = [
            f"  {i + 1}. PID {pid} — config: {config_path}"
            for i, (pid, config_path) in enumerate(processes)
        ]
        self._output_stream.write("\n".join([header] + entries) + "\n")
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
                return "Cancelled."

            if 1 <= choice <= len(processes):
                pid, config_path = processes[choice - 1]
                subprocess.run(["kill", pid])
                return f"Stopped monitor process PID {pid} (config: {config_path})."

            self._output_stream.write(
                f"Invalid choice. Enter a number between 0 and {len(processes)}.\n"
            )
            self._output_stream.flush()
