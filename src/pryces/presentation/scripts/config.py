import json
from dataclasses import dataclass
from pathlib import Path

from .exceptions import ConfigLoadingFailed


@dataclass(frozen=True, slots=True)
class MonitorStocksConfig:
    duration: int
    interval: int
    symbols: list[str]

    def __post_init__(self) -> None:
        if not isinstance(self.duration, int) or self.duration <= 0:
            raise ValueError("duration must be a positive integer")
        if not isinstance(self.interval, int) or self.interval <= 0:
            raise ValueError("interval must be a positive integer")
        if not isinstance(self.symbols, list) or not self.symbols:
            raise ValueError("symbols must be a non-empty list")


class ConfigManager:
    def __init__(self, path: Path) -> None:
        self._path = path

    def load_monitor_stocks_config(self) -> MonitorStocksConfig:
        try:
            data = json.loads(self._path.read_text())
            return MonitorStocksConfig(**data)
        except FileNotFoundError:
            raise ConfigLoadingFailed(f"config file not found: {self._path}")
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            raise ConfigLoadingFailed(f"invalid config file: {e}")
        except Exception as e:
            raise ConfigLoadingFailed(f"unexpected error loading config: {e}")
