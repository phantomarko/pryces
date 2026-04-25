from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from .exceptions import ConfigLoadingFailed

CONFIGS_DIR = Path(__file__).resolve().parents[3] / "configs"


@dataclass(frozen=True, slots=True)
class SymbolConfig:
    symbol: str
    prices: list[Decimal]


@dataclass(frozen=True, slots=True)
class MonitorStocksConfig:
    interval: int
    symbols: list[SymbolConfig]

    def __post_init__(self) -> None:
        if not isinstance(self.interval, int) or self.interval <= 0:
            raise ValueError("interval must be a positive integer")
        if not isinstance(self.symbols, list) or not self.symbols:
            raise ValueError("symbols must be a non-empty list")


class ConfigManager:
    def __init__(self, path: Path) -> None:
        self._path = path

    def write_monitor_stocks_config(self, config: MonitorStocksConfig) -> None:
        data = {
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
                interval=data["interval"],
                symbols=symbols,
            )
        except FileNotFoundError as e:
            raise ConfigLoadingFailed(f"config file not found: {self._path}") from e
        except (json.JSONDecodeError, TypeError, ValueError, KeyError) as e:
            raise ConfigLoadingFailed(f"invalid config file: {e}") from e
        except Exception as e:
            raise ConfigLoadingFailed(f"unexpected error loading config: {e}") from e

    def replace_symbol_prices(self, symbol: str, prices: list[Decimal]) -> None:
        config = self.read_monitor_stocks_config()
        updated = [
            SymbolConfig(symbol=sc.symbol, prices=prices) if sc.symbol == symbol else sc
            for sc in config.symbols
        ]
        self.write_monitor_stocks_config(
            MonitorStocksConfig(interval=config.interval, symbols=updated)
        )

    def add_symbol(self, symbol: str) -> None:
        config = self.read_monitor_stocks_config()
        updated = config.symbols + [SymbolConfig(symbol=symbol, prices=[])]
        self.write_monitor_stocks_config(
            MonitorStocksConfig(interval=config.interval, symbols=updated)
        )

    def remove_symbol(self, symbol: str) -> None:
        config = self.read_monitor_stocks_config()
        updated = [sc for sc in config.symbols if sc.symbol != symbol]
        self.write_monitor_stocks_config(
            MonitorStocksConfig(interval=config.interval, symbols=updated)
        )


def find_config_by_name(config_name: str) -> tuple[Path, MonitorStocksConfig] | None:
    if not CONFIGS_DIR.exists():
        return None
    path = CONFIGS_DIR / f"{config_name}.json"
    try:
        return path, ConfigManager(path).read_monitor_stocks_config()
    except ConfigLoadingFailed:
        return None


def find_config_for_symbol(symbol: str) -> tuple[Path, MonitorStocksConfig] | None:
    if not CONFIGS_DIR.exists():
        return None
    for path in sorted(CONFIGS_DIR.glob("*.json")):
        try:
            config = ConfigManager(path).read_monitor_stocks_config()
            if any(s.symbol == symbol.upper() for s in config.symbols):
                return path, config
        except ConfigLoadingFailed:
            continue
    return None


def get_config_names() -> list[str]:
    if not CONFIGS_DIR.exists():
        return []
    return sorted(path.stem for path in CONFIGS_DIR.glob("*.json"))


def get_all_tracked_symbols() -> list[str]:
    if not CONFIGS_DIR.exists():
        return []
    symbols: set[str] = set()
    for path in CONFIGS_DIR.glob("*.json"):
        try:
            config = ConfigManager(path).read_monitor_stocks_config()
            for sc in config.symbols:
                symbols.add(sc.symbol)
        except ConfigLoadingFailed:
            continue
    return sorted(symbols)


def get_all_tracked_symbols_with_targets() -> list[tuple[str, list[Decimal]]]:
    if not CONFIGS_DIR.exists():
        return []
    symbols: dict[str, list[Decimal]] = {}
    for path in sorted(CONFIGS_DIR.glob("*.json")):
        try:
            config = ConfigManager(path).read_monitor_stocks_config()
            for sc in config.symbols:
                if sc.symbol not in symbols:
                    symbols[sc.symbol] = sc.prices
        except ConfigLoadingFailed:
            continue
    return [(s, symbols[s]) for s in sorted(symbols)]
