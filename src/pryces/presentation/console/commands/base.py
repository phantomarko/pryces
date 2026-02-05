from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class CommandMetadata:
    id: str
    name: str
    description: str


@dataclass(frozen=True)
class InputPrompt:
    key: str
    prompt: str
    validator: Callable[[str], bool] | None = None


class Command(ABC):
    @abstractmethod
    def get_metadata(self) -> CommandMetadata:
        pass

    @abstractmethod
    def get_input_prompts(self) -> list[InputPrompt]:
        pass

    @abstractmethod
    def execute(self, **kwargs) -> str:
        pass
