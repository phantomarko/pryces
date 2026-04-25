from pryces.infrastructure.configs import ConfigStore, MonitorStocksConfig

from .base import Command, CommandMetadata, CommandResult, InputPrompt
from ..utils import (
    parse_symbols_with_targets,
    validate_positive_integer,
    validate_symbols_with_targets,
)


class CreateConfigCommand(Command):
    def __init__(self, config_store: ConfigStore) -> None:
        self._config_store = config_store

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
                validator=self._config_store.validate_name,
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
        config = MonitorStocksConfig(
            interval=int(interval),
            symbols=parse_symbols_with_targets(symbols),
        )
        path = self._config_store.create(name, config)
        return CommandResult(f"Config created: {path}")
