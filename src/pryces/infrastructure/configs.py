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


class ConfigStore:
    def __init__(self, configs_dir: Path) -> None:
        self._configs_dir = configs_dir

    def list_paths(self) -> list[Path]:
        if not self._configs_dir.exists():
            return []
        return sorted(self._configs_dir.glob("*.json"))

    def list_names(self) -> list[str]:
        return [path.stem for path in self.list_paths()]

    def find_by_name(self, name: str) -> tuple[Path, MonitorStocksConfig] | None:
        if not self._configs_dir.exists():
            return None
        path = self._configs_dir / f"{name}.json"
        try:
            return path, ConfigManager(path).read_monitor_stocks_config()
        except ConfigLoadingFailed:
            return None

    def find_for_symbol(self, symbol: str) -> tuple[Path, MonitorStocksConfig] | None:
        for path in self.list_paths():
            try:
                config = ConfigManager(path).read_monitor_stocks_config()
                if any(s.symbol == symbol.upper() for s in config.symbols):
                    return path, config
            except ConfigLoadingFailed:
                continue
        return None

    def list_tracked_symbols(self) -> list[str]:
        symbols: set[str] = set()
        for path in self.list_paths():
            try:
                config = ConfigManager(path).read_monitor_stocks_config()
                for sc in config.symbols:
                    symbols.add(sc.symbol)
            except ConfigLoadingFailed:
                continue
        return sorted(symbols)

    def list_tracked_symbols_with_targets(self) -> list[tuple[str, list[Decimal]]]:
        symbols: dict[str, list[Decimal]] = {}
        for path in self.list_paths():
            try:
                config = ConfigManager(path).read_monitor_stocks_config()
                for sc in config.symbols:
                    if sc.symbol not in symbols:
                        symbols[sc.symbol] = sc.prices
            except ConfigLoadingFailed:
                continue
        return [(s, symbols[s]) for s in sorted(symbols)]

    def validate_name(self, name: str) -> str | None:
        if not name or not name.strip():
            return "Name must not be empty."
        stripped = name.strip()
        if "/" in stripped or "." in stripped:
            return "Name must not contain '/' or '.'."
        if (self._configs_dir / f"{stripped}.json").exists():
            return f"Config '{stripped}.json' already exists."
        return None

    def create(self, name: str, config: MonitorStocksConfig) -> Path:
        self._configs_dir.mkdir(parents=True, exist_ok=True)
        path = self._configs_dir / f"{name.strip()}.json"
        ConfigManager(path).write_monitor_stocks_config(config)
        return path

    def delete_by_path(self, path: Path) -> None:
        path.unlink()
