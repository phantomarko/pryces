from .base import Command, CommandMetadata, InputPrompt
from ..utils import get_running_monitors


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
        processes = get_running_monitors()

        if not processes:
            return "No monitor processes found."

        header = f"Found {len(processes)} monitor process(es):"
        entries = [
            f"  {i + 1}. PID {pid} — config: {config_path}"
            for i, (pid, config_path) in enumerate(processes)
        ]
        return "\n".join([header] + entries)
