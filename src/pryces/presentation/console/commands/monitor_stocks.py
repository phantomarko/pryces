import subprocess
import sys

from .base import Command, CommandMetadata, InputPrompt
from ..utils import validate_file_path


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
        ]

    def execute(self, config_path: str = None, **kwargs) -> str:
        cmd = [
            sys.executable,
            "-m",
            "pryces.presentation.scripts.monitor_stocks",
            config_path.strip(),
        ]
        process = subprocess.Popen(
            cmd,
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return f"Monitor started in background (PID: {process.pid})"
