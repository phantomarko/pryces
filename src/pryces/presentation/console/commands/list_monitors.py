from .base import Command, CommandMetadata, CommandResult, InputPrompt
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

    def execute(self, **kwargs) -> CommandResult:
        processes = get_running_monitors()

        if not processes:
            return CommandResult(message="No monitor processes found.")

        header = f"Found {len(processes)} monitor process(es):"
        entries = [
            f"  {i + 1}. PID {pid} — config: {config_path}"
            for i, (pid, config_path) in enumerate(processes)
        ]
        return CommandResult(message="\n".join([header] + entries))
