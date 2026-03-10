from pathlib import Path

from pryces.presentation.scripts.config import ConfigManager, MonitorStocksConfig

from .base import Command, CommandMetadata, CommandResult, InputPrompt
from ..utils import (
    create_config_selection_validator,
    format_config_details,
    get_config_files,
    parse_symbols_with_targets,
    validate_positive_integer,
    validate_symbols_with_targets,
)


def _validate_operation(value: str) -> str | None:
    if value.strip() in ("1", "2"):
        return None
    return "Enter 1 (interval) or 2 (symbols and targets)."


def _validate_new_value(value: str) -> str | None:
    if not value or not value.strip():
        return "Value must not be empty."
    return None


class EditConfigCommand(Command):
    def __init__(self) -> None:
        self._config_files: list[Path] = []

    def get_metadata(self) -> CommandMetadata:
        return CommandMetadata(
            id="edit_config",
            name="Edit Config",
            description="Edit an existing monitoring config",
            show_progress=False,
        )

    def get_input_prompts(self) -> list[InputPrompt]:
        self._config_files = get_config_files()
        if not self._config_files:
            return []

        count = len(self._config_files)
        details_parts = []
        for i, path in enumerate(self._config_files):
            try:
                config = ConfigManager(path).read_monitor_stocks_config()
                details_parts.append(format_config_details(config, path.name, i + 1))
            except Exception:
                details_parts.append(f"{i + 1}. {path.name} (failed to load)")
        preamble = f"Found {count} config(s):\n\n" + "\n\n".join(details_parts) + "\n"
        return [
            InputPrompt(
                key="config_selection",
                prompt=f"Select config (1-{count}): ",
                validator=create_config_selection_validator(count),
                preamble=preamble,
            ),
            InputPrompt(
                key="operation",
                prompt="What to edit (1 or 2): ",
                validator=_validate_operation,
                preamble="What to edit: 1=interval  2=symbols and targets",
            ),
            InputPrompt(
                key="new_value",
                prompt="New value: ",
                validator=_validate_new_value,
                preamble=(
                    "For interval: enter a positive integer (e.g. 60)\n"
                    "For symbols: enter space-separated tokens (e.g. AAPL MSFT:150,155 GOOG)"
                ),
            ),
        ]

    def execute(self, **kwargs) -> CommandResult:
        if not self._config_files:
            return CommandResult("No configs found. Create one first.", success=False)

        config_selection = kwargs.get("config_selection")
        operation = kwargs.get("operation", "").strip()
        new_value = kwargs.get("new_value", "").strip()

        path = self._config_files[int(config_selection) - 1]
        manager = ConfigManager(path)

        try:
            config = manager.read_monitor_stocks_config()
        except Exception as e:
            return CommandResult(f"Failed to load config: {e}", success=False)

        if operation == "1":
            if validate_positive_integer(new_value) is not None:
                return CommandResult("Invalid interval. Must be a positive integer.", success=False)
            updated = MonitorStocksConfig(interval=int(new_value), symbols=config.symbols)
        else:
            if validate_symbols_with_targets(new_value) is not None:
                return CommandResult(
                    "Invalid symbols format. Use: SYMBOL or SYMBOL:P1,P2 separated by spaces.",
                    success=False,
                )
            updated = MonitorStocksConfig(
                interval=config.interval, symbols=parse_symbols_with_targets(new_value)
            )

        manager.write_monitor_stocks_config(updated)
        return CommandResult(f"Config updated: {path.name}")
