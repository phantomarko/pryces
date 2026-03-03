import json
import logging
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from ...application.dtos import TargetPriceDTO
from .exceptions import ConfigLoadingFailed


@dataclass(frozen=True, slots=True)
class SymbolConfig:
    symbol: str
    prices: list[Decimal]


@dataclass(frozen=True, slots=True)
class MonitorStocksConfig:
    duration: int
    interval: int
    symbols: list[SymbolConfig]

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

    def write_monitor_stocks_config(self, config: MonitorStocksConfig) -> None:
        data = {
            "duration": config.duration,
            "interval": config.interval,
            "symbols": [
                {"symbol": s.symbol, "prices": [float(p) for p in s.prices]} for s in config.symbols
            ],
        }
        self._path.write_text(json.dumps(data, indent=2))

    def read_monitor_stocks_config(self) -> MonitorStocksConfig:
        try:
            data = json.loads(self._path.read_text())
            symbols = [
                SymbolConfig(
                    symbol=s["symbol"],
                    prices=[Decimal(str(p)) for p in s["prices"]],
                )
                for s in data["symbols"]
            ]
            return MonitorStocksConfig(
                duration=data["duration"],
                interval=data["interval"],
                symbols=symbols,
            )
        except FileNotFoundError:
            raise ConfigLoadingFailed(f"config file not found: {self._path}")
        except (json.JSONDecodeError, TypeError, ValueError, KeyError) as e:
            raise ConfigLoadingFailed(f"invalid config file: {e}")
        except Exception as e:
            raise ConfigLoadingFailed(f"unexpected error loading config: {e}")


class ConfigRefresher:
    def __init__(self, config_manager: ConfigManager, config: MonitorStocksConfig) -> None:
        self._config_manager = config_manager
        self._config = config
        self._logger = logging.getLogger(__name__)

    @property
    def config(self) -> MonitorStocksConfig:
        return self._config

    def refresh(self) -> None:
        try:
            new_config = self._config_manager.read_monitor_stocks_config()
            if new_config != self._config:
                self._config = new_config
                self._logger.info("Config refreshed.")
                self.log_config()
        except Exception as e:
            self._logger.warning(f"Config refresh failed: {e}")

    def remove_fulfilled_targets(self, fulfilled: list[TargetPriceDTO]) -> None:
        if not fulfilled:
            return

        self._logger.info(
            f"Fulfilled targets: {', '.join(f'{tp.symbol}@{tp.target}' for tp in fulfilled)}"
        )
        fulfilled_pairs = {(tp.symbol, tp.target) for tp in fulfilled}
        updated_symbols = [
            SymbolConfig(
                symbol=sc.symbol,
                prices=[p for p in sc.prices if (sc.symbol, p) not in fulfilled_pairs],
            )
            for sc in self._config.symbols
        ]

        if updated_symbols == self._config.symbols:
            return

        new_config = MonitorStocksConfig(
            duration=self._config.duration,
            interval=self._config.interval,
            symbols=updated_symbols,
        )
        self._config = new_config
        self._config_manager.write_monitor_stocks_config(new_config)
        self._logger.info("Removing fulfilled targets from config.")
        self.log_config()

    def log_config(self) -> None:
        duration_label = (
            f"{self._config.duration} minute{'s' if self._config.duration != 1 else ''}"
        )
        self._logger.info(f"Monitoring every {self._config.interval}s for {duration_label}.")
        stocks_info = [
            f"{s.symbol} @ {', '.join(str(p) for p in s.prices)}" if s.prices else s.symbol
            for s in self._config.symbols
        ]
        self._logger.info(f"Stocks: {' | '.join(stocks_info)}")
