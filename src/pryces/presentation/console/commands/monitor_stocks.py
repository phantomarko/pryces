import subprocess
import sys
from pathlib import Path

from pryces.infrastructure.configs import ConfigStore

from .base import Command, CommandMetadata, CommandResult, InputPrompt
from ..utils import (
    create_config_selection_validator,
    format_config_list,
    validate_non_negative_integer,
    validate_positive_integer,
)


class MonitorStocksCommand(Command):
    def __init__(self, config_store: ConfigStore) -> None:
        self._config_store = config_store
        self._config_files: list[Path] = []

    def get_metadata(self) -> CommandMetadata:
        return CommandMetadata(
            id="monitor_stocks",
            name="Execute Monitor Process",
            description="Monitor stocks for relevant price notifications",
            show_progress=False,
        )

    def get_input_prompts(self) -> list[InputPrompt]:
        self._config_files = self._config_store.list_paths()
        if not self._config_files:
            return []

        count = len(self._config_files)
        return [
            InputPrompt(
                key="config_selection",
                prompt=f"Select config (1-{count}): ",
                validator=create_config_selection_validator(count),
                preamble=format_config_list(self._config_files),
            ),
            InputPrompt(
                key="duration",
                prompt="Monitoring duration in minutes: ",
                validator=validate_positive_integer,
            ),
            InputPrompt(
                key="extra_delay",
                prompt="Extra price delay in minutes [0]: ",
                validator=validate_non_negative_integer,
                default="0",
            ),
        ]

    def execute(
        self,
        config_selection: str = None,
        duration: str = None,
        extra_delay: str = "",
        **kwargs,
    ) -> CommandResult:
        if not self._config_files:
            return CommandResult("No configs found. Create one first.", success=False)

        config_path = str(self._config_files[int(config_selection) - 1])
        extra_delay_minutes = int(extra_delay.strip()) if extra_delay.strip() else 0
        cmd = [
            sys.executable,
            "-m",
            "pryces.presentation.scripts.monitor_stocks",
            config_path,
            "--duration",
            str(int(duration)),
            "--extra-delay",
            str(extra_delay_minutes),
        ]
        try:
            process = subprocess.Popen(
                cmd,
                start_new_session=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except OSError as e:
            return CommandResult(message=f"Failed to start monitor process: {e}", success=False)
        return CommandResult(message=f"Monitor started in background (PID: {process.pid})")
