"""Base command interface for console commands."""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class CommandMetadata:
    """Metadata describing a command for menu display."""
    id: str
    name: str
    description: str


@dataclass(frozen=True)
class InputPrompt:
    """Specification for collecting input from user."""
    key: str
    prompt: str
    validator: Callable[[str], bool] | None = None


class Command(ABC):
    """Base interface for all console commands."""

    @abstractmethod
    def get_metadata(self) -> CommandMetadata:
        """Return metadata describing this command."""
        pass

    @abstractmethod
    def get_input_prompts(self) -> list[InputPrompt]:
        """Return list of input prompts needed to execute this command."""
        pass

    @abstractmethod
    def execute(self, **kwargs) -> str:
        """Execute the command with provided arguments.

        Returns:
            JSON string with command output
        """
        pass
