from pryces.infrastructure.configs import ConfigManager, MonitorStocksConfig

from .base import Command, CommandMetadata, CommandResult, InputPrompt
from ..utils import (
    CONFIGS_DIR,
    parse_symbols_with_targets,
    validate_positive_integer,
    validate_symbols_with_targets,
)


def _validate_config_name(value: str) -> str | None:
    if not value or not value.strip():
        return "Name must not be empty."
    name = value.strip()
    if "/" in name or "." in name:
        return "Name must not contain '/' or '.'."
    if (CONFIGS_DIR / f"{name}.json").exists():
        return f"Config '{name}.json' already exists."
    return None


class CreateConfigCommand(Command):
    def get_metadata(self) -> CommandMetadata:
        return CommandMetadata(
            id="create_config",
            name="Create Config",
            description="Create a new monitoring config",
            show_progress=False,
        )

    def get_input_prompts(self) -> list[InputPrompt]:
        return [
            InputPrompt(
                key="name",
                prompt="Config name (without .json): ",
                validator=_validate_config_name,
            ),
            InputPrompt(
                key="interval",
                prompt="Interval in seconds: ",
                validator=validate_positive_integer,
            ),
            InputPrompt(
                key="symbols",
                prompt="Symbols (e.g. AAPL MSFT:150,155 GOOG): ",
                validator=validate_symbols_with_targets,
            ),
        ]

    def execute(
        self, name: str = None, interval: str = None, symbols: str = None, **kwargs
    ) -> CommandResult:
        CONFIGS_DIR.mkdir(parents=True, exist_ok=True)
        path = CONFIGS_DIR / f"{name.strip()}.json"
        config = MonitorStocksConfig(
            interval=int(interval),
            symbols=parse_symbols_with_targets(symbols),
        )
        ConfigManager(path).write_monitor_stocks_config(config)
        return CommandResult(f"Config created: {path}")
