from pathlib import Path

from pryces.infrastructure.configs import ConfigStore

from .base import Command, CommandMetadata, CommandResult, InputPrompt
from ..utils import create_config_selection_validator, format_config_list


def _validate_confirm(value: str) -> str | None:
    if value.strip().lower() in ("yes", "no"):
        return None
    return "Enter 'yes' to confirm or 'no' to cancel."


class DeleteConfigCommand(Command):
    def __init__(self, config_store: ConfigStore) -> None:
        self._config_store = config_store
        self._config_files: list[Path] = []

    def get_metadata(self) -> CommandMetadata:
        return CommandMetadata(
            id="delete_config",
            name="Delete Config",
            description="Delete an existing monitoring config",
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
                prompt=f"Select config to delete (1-{count}): ",
                validator=create_config_selection_validator(count),
                preamble=format_config_list(self._config_files),
            ),
            InputPrompt(
                key="confirm",
                prompt="Type 'yes' to confirm deletion: ",
                validator=_validate_confirm,
                preamble=None,
            ),
        ]

    def execute(self, **kwargs) -> CommandResult:
        if not self._config_files:
            return CommandResult("No configs found.", success=False)

        config_selection = kwargs.get("config_selection")
        confirm = kwargs.get("confirm", "").strip().lower()

        path = self._config_files[int(config_selection) - 1]

        if confirm != "yes":
            return CommandResult("Deletion cancelled.")

        self._config_store.delete_by_path(path)
        return CommandResult(f"Config deleted: {path.name}")
