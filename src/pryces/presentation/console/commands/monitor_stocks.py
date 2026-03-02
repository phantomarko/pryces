import subprocess
import sys

from .base import Command, CommandMetadata, CommandResult, InputPrompt
from ..utils import validate_file_path, validate_non_negative_integer


class MonitorStocksCommand(Command):
    def get_metadata(self) -> CommandMetadata:
        return CommandMetadata(
            id="monitor_stocks",
            name="Monitor Stocks",
            description="Monitor stocks for relevant price notifications",
        )

    def get_input_prompts(self) -> list[InputPrompt]:
        return [
            InputPrompt(
                key="config_path",
                prompt="Enter the path to the JSON config file (e.g., monitor.json): ",
                validator=validate_file_path,
            ),
            InputPrompt(
                key="extra_delay",
                prompt="Extra price delay in minutes [0]: ",
                validator=validate_non_negative_integer,
            ),
        ]

    def execute(self, config_path: str = None, extra_delay: str = "", **kwargs) -> CommandResult:
        extra_delay_minutes = int(extra_delay.strip()) if extra_delay.strip() else 0
        cmd = [
            sys.executable,
            "-m",
            "pryces.presentation.scripts.monitor_stocks",
            config_path.strip(),
            "--extra-delay",
            str(extra_delay_minutes),
        ]
        process = subprocess.Popen(
            cmd,
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return CommandResult(message=f"Monitor started in background (PID: {process.pid})")
