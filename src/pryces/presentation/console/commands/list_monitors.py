import subprocess

from .base import Command, CommandMetadata, InputPrompt

_MODULE = "pryces.presentation.scripts.monitor_stocks"


class ListMonitorsCommand(Command):
    def get_metadata(self) -> CommandMetadata:
        return CommandMetadata(
            id="list_monitors",
            name="List Monitor Processes",
            description="List running monitor processes",
        )

    def get_input_prompts(self) -> list[InputPrompt]:
        return []

    def execute(self, **kwargs) -> str:
        result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
        lines = result.stdout.splitlines()

        processes = []
        for line in lines:
            if _MODULE in line and "ps aux" not in line and "/bin/sh" not in line:
                parts = line.split()
                pid = parts[1]
                try:
                    module_index = parts.index("-m") + 2
                    config_path = parts[module_index] if module_index < len(parts) else "unknown"
                except ValueError:
                    config_path = "unknown"
                processes.append(f"  PID {pid} — config: {config_path}")

        if not processes:
            return "No monitor processes found."

        header = f"Found {len(processes)} monitor process(es):"
        return "\n".join([header] + processes)
