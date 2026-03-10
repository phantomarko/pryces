from pryces.presentation.scripts.config import ConfigManager

from .base import Command, CommandMetadata, CommandResult, InputPrompt
from ..utils import CONFIGS_DIR, format_config_details, get_config_files


class ListConfigsCommand(Command):
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
        paths = get_config_files()
        if not paths:
            return CommandResult(f"No configs found in {CONFIGS_DIR.name}/.")

        parts = []
        for path in paths:
            try:
                config = ConfigManager(path).read_monitor_stocks_config()
                parts.append(format_config_details(config, path.name))
            except Exception as e:
                parts.append(f"{path.name}: error loading config — {e}")

        return CommandResult("\n\n".join(parts))
