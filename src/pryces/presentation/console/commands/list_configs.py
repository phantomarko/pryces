from pryces.infrastructure.configs import ConfigManager, ConfigStore

from .base import Command, CommandMetadata, CommandResult, InputPrompt
from ..utils import format_config_details


class ListConfigsCommand(Command):
    def __init__(self, config_store: ConfigStore) -> None:
        self._config_store = config_store

    def get_metadata(self) -> CommandMetadata:
        return CommandMetadata(
            id="list_configs",
            name="List Configs",
            description="List all monitoring configs",
            show_progress=False,
        )

    def get_input_prompts(self) -> list[InputPrompt]:
        return []

    def execute(self, **kwargs) -> CommandResult:
        paths = self._config_store.list_paths()
        if not paths:
            return CommandResult("No configs found.")

        parts = []
        for i, path in enumerate(paths):
            try:
                config = ConfigManager(path).read_monitor_stocks_config()
                parts.append(format_config_details(config, path.name, i + 1))
            except Exception as e:
                parts.append(f"{i + 1}. {path.name}: error loading config — {e}")

        return CommandResult("\n\n".join(parts))
