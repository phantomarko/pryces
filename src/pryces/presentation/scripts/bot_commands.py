from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from decimal import Decimal
from pathlib import Path

from ...application.dtos import StockStatisticsDTO
from ...application.interfaces import LoggerFactory
from .config import ConfigManager, MonitorStocksConfig, SymbolConfig

_MAX_MESSAGE_LENGTH = 256
_MAX_INTEGER_DIGITS = 7
_MAX_DECIMAL_DIGITS = 8


def _validate_price(raw: str) -> Decimal | str:
    if not raw or raw[0] == "-":
        return "❌ Invalid price"
    parts = raw.split(".")
    if len(parts) > 2:
        return "❌ Invalid price"
    if not all(part.isdigit() for part in parts if part):
        return "❌ Invalid price"
    integer_part = parts[0] or "0"
    decimal_part = parts[1] if len(parts) == 2 else ""
    if len(integer_part) > _MAX_INTEGER_DIGITS:
        return "❌ Invalid price"
    if len(decimal_part) > _MAX_DECIMAL_DIGITS:
        return "❌ Invalid price"
    value = Decimal(raw)
    if value <= 0:
        return "❌ Invalid price"
    return value


class BotCommand(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def usage(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @property
    @abstractmethod
    def arg_count(self) -> int:
        pass

    @abstractmethod
    def execute(self, args: list[str]) -> str:
        pass


_FindConfigFn = Callable[[str], tuple[Path, MonitorStocksConfig] | None]
_FindConfigByNameFn = Callable[[str], tuple[Path, MonitorStocksConfig] | None]
_GetAllSymbolsFn = Callable[[], list[str]]
_GetAllSymbolsWithTargetsFn = Callable[[], list[tuple[str, list[Decimal]]]]
_GetConfigNamesFn = Callable[[], list[str]]
_GetStockStatisticsFn = Callable[[str], StockStatisticsDTO | None]


def _find_symbol_config(
    find_config: _FindConfigFn, symbol: str
) -> tuple[Path, MonitorStocksConfig, SymbolConfig] | str:
    result = find_config(symbol)
    if result is None:
        return f"❌ {symbol} is not tracked"
    path, config = result
    for sc in config.symbols:
        if sc.symbol == symbol:
            return path, config, sc
    return f"{symbol} is not tracked"


def _update_symbol_prices(
    path: Path, config: MonitorStocksConfig, symbol: str, new_prices: list[Decimal]
) -> None:
    updated_symbols = [
        SymbolConfig(symbol=sc.symbol, prices=new_prices) if sc.symbol == symbol else sc
        for sc in config.symbols
    ]
    new_config = MonitorStocksConfig(interval=config.interval, symbols=updated_symbols)
    ConfigManager(path).write_monitor_stocks_config(new_config)


def _add_symbol_to_config(path: Path, config: MonitorStocksConfig, symbol: str) -> None:
    updated = config.symbols + [SymbolConfig(symbol=symbol, prices=[])]
    ConfigManager(path).write_monitor_stocks_config(
        MonitorStocksConfig(interval=config.interval, symbols=updated)
    )


def _remove_symbol_from_config(path: Path, config: MonitorStocksConfig, symbol: str) -> None:
    updated = [sc for sc in config.symbols if sc.symbol != symbol]
    ConfigManager(path).write_monitor_stocks_config(
        MonitorStocksConfig(interval=config.interval, symbols=updated)
    )


class TargetsCommand(BotCommand):
    def __init__(self, find_config: _FindConfigFn) -> None:
        self._find_config = find_config

    @property
    def name(self) -> str:
        return "/targets"

    @property
    def usage(self) -> str:
        return "/targets <symbol>"

    @property
    def description(self) -> str:
        return "List all target prices for a symbol"

    @property
    def arg_count(self) -> int:
        return 1

    def execute(self, args: list[str]) -> str:
        symbol = args[0].upper()
        try:
            result = _find_symbol_config(self._find_config, symbol)
            if isinstance(result, str):
                return result
            _, _, sc = result
            if not sc.prices:
                return f"🎯 {symbol} targets: none"
            prices_str = ", ".join(str(p) for p in sc.prices)
            return f"🎯 {symbol} targets: {prices_str}"
        except Exception as e:
            return f"❌ Error: {e}"


class TargetAddCommand(BotCommand):
    def __init__(self, find_config: _FindConfigFn) -> None:
        self._find_config = find_config

    @property
    def name(self) -> str:
        return "/target_add"

    @property
    def usage(self) -> str:
        return "/target_add <symbol> <price>"

    @property
    def description(self) -> str:
        return "Add a target price to a symbol"

    @property
    def arg_count(self) -> int:
        return 2

    def execute(self, args: list[str]) -> str:
        symbol = args[0].upper()
        result = _validate_price(args[1])
        if isinstance(result, str):
            return result
        price = result

        try:
            config_result = _find_symbol_config(self._find_config, symbol)
            if isinstance(config_result, str):
                return config_result
            path, config, sc = config_result
            if price in sc.prices:
                return f"ℹ️ {symbol} already has target {price}"
            _update_symbol_prices(path, config, symbol, sc.prices + [price])
            return f"✅ Added target {price} to {symbol}"
        except Exception as e:
            return f"❌ Error: {e}"


class TargetRemoveCommand(BotCommand):
    def __init__(self, find_config: _FindConfigFn) -> None:
        self._find_config = find_config

    @property
    def name(self) -> str:
        return "/target_remove"

    @property
    def usage(self) -> str:
        return "/target_remove <symbol> <price>"

    @property
    def description(self) -> str:
        return "Remove a target price from a symbol"

    @property
    def arg_count(self) -> int:
        return 2

    def execute(self, args: list[str]) -> str:
        symbol = args[0].upper()
        result = _validate_price(args[1])
        if isinstance(result, str):
            return result
        price = result

        try:
            config_result = _find_symbol_config(self._find_config, symbol)
            if isinstance(config_result, str):
                return config_result
            path, config, sc = config_result
            if price not in sc.prices:
                return f"ℹ️ {symbol} does not have target {price}"
            _update_symbol_prices(path, config, symbol, [p for p in sc.prices if p != price])
            return f"✅ Removed target {price} from {symbol}"
        except Exception as e:
            return f"❌ Error: {e}"


class SymbolAddCommand(BotCommand):
    def __init__(self, find_config_by_name: _FindConfigByNameFn) -> None:
        self._find_config_by_name = find_config_by_name

    @property
    def name(self) -> str:
        return "/symbol_add"

    @property
    def usage(self) -> str:
        return "/symbol_add <symbol> <config>"

    @property
    def description(self) -> str:
        return "Add a symbol to a config"

    @property
    def arg_count(self) -> int:
        return 2

    def execute(self, args: list[str]) -> str:
        symbol = args[0].upper()
        config_name = args[1]
        try:
            result = self._find_config_by_name(config_name)
            if result is None:
                return f"❌ Config {config_name} not found"
            path, config = result
            if any(sc.symbol == symbol for sc in config.symbols):
                return f"ℹ️ {symbol} is already in {config_name}"
            _add_symbol_to_config(path, config, symbol)
            return f"✅ Added {symbol} to {config_name}"
        except Exception as e:
            return f"❌ Error: {e}"


class SymbolRemoveCommand(BotCommand):
    def __init__(self, find_config: _FindConfigFn) -> None:
        self._find_config = find_config

    @property
    def name(self) -> str:
        return "/symbol_remove"

    @property
    def usage(self) -> str:
        return "/symbol_remove <symbol>"

    @property
    def description(self) -> str:
        return "Remove a symbol from its config"

    @property
    def arg_count(self) -> int:
        return 1

    def execute(self, args: list[str]) -> str:
        symbol = args[0].upper()
        try:
            result = self._find_config(symbol)
            if result is None:
                return f"❌ {symbol} is not tracked"
            path, config = result
            if len(config.symbols) == 1:
                return "⚠️ Cannot remove the last symbol from a config"
            _remove_symbol_from_config(path, config, symbol)
            return f"✅ Removed {symbol} from config"
        except Exception as e:
            return f"❌ Error: {e}"


class SymbolsCommand(BotCommand):
    def __init__(self, get_all_symbols_with_targets: _GetAllSymbolsWithTargetsFn) -> None:
        self._get_all_symbols_with_targets = get_all_symbols_with_targets

    @property
    def name(self) -> str:
        return "/symbols"

    @property
    def usage(self) -> str:
        return "/symbols"

    @property
    def description(self) -> str:
        return "List all tracked symbols and their targets"

    @property
    def arg_count(self) -> int:
        return 0

    def execute(self, args: list[str]) -> str:
        symbols = self._get_all_symbols_with_targets()
        if not symbols:
            return "📋 No symbols tracked"
        lines = ["📋 Symbols & targets:"]
        for i, (symbol, prices) in enumerate(symbols, start=1):
            if prices:
                prices_str = ", ".join(str(p) for p in prices)
                lines.append(f"{i}) {symbol} — 🎯 {prices_str}")
            else:
                lines.append(f"{i}) {symbol}")
        return "\n".join(lines)


def _format_stats(dto: StockStatisticsDTO) -> str:
    header = f"📊 {dto.symbol} — {dto.current_price:.2f}"
    if dto.currency:
        header += f" {dto.currency}"
    lines = [header]
    if not dto.price_changes:
        lines.append("No historical data available")
        return "\n".join(lines)
    for pc in dto.price_changes:
        sign = "+" if pc.change_percentage > 0 else ""
        pct_str = f"{sign}{pc.change_percentage:.2f}%"
        icon = "📈" if pc.change_percentage >= 0 else "📉"
        lines.append(f"{icon} {pc.period:<3}  {pc.close_price:.2f}  {pct_str}")
    return "\n".join(lines)


class StatsCommand(BotCommand):
    def __init__(self, get_stock_statistics: _GetStockStatisticsFn) -> None:
        self._get_stock_statistics = get_stock_statistics

    @property
    def name(self) -> str:
        return "/stats"

    @property
    def usage(self) -> str:
        return "/stats <symbol>"

    @property
    def description(self) -> str:
        return "Show price statistics for a symbol"

    @property
    def arg_count(self) -> int:
        return 1

    def execute(self, args: list[str]) -> str:
        symbol = args[0].upper()
        try:
            dto = self._get_stock_statistics(symbol)
            if dto is None:
                return f"❌ {symbol} not found"
            return _format_stats(dto)
        except Exception as e:
            return f"❌ Error: {e}"


class ConfigsCommand(BotCommand):
    def __init__(self, get_config_names: _GetConfigNamesFn) -> None:
        self._get_config_names = get_config_names

    @property
    def name(self) -> str:
        return "/configs"

    @property
    def usage(self) -> str:
        return "/configs"

    @property
    def description(self) -> str:
        return "List all config files"

    @property
    def arg_count(self) -> int:
        return 0

    def execute(self, args: list[str]) -> str:
        names = self._get_config_names()
        if not names:
            return "🗂️ No configs found"
        return f"🗂️ {', '.join(names)}"


class HelpCommand(BotCommand):
    def __init__(self, commands: list[BotCommand]) -> None:
        self._commands = commands

    @property
    def name(self) -> str:
        return "/help"

    @property
    def usage(self) -> str:
        return "/help"

    @property
    def description(self) -> str:
        return "Show all commands with usage"

    @property
    def arg_count(self) -> int:
        return 0

    def execute(self, args: list[str]) -> str:
        lines = ["📖 Commands:"]
        lines.extend(f"{cmd.usage} — {cmd.description}" for cmd in self._commands)
        return "\n".join(lines)


class BotCommandDispatcher:
    def __init__(self, commands: list[BotCommand], logger_factory: LoggerFactory) -> None:
        self._commands = {cmd.name: cmd for cmd in commands}
        self._logger = logger_factory.get_logger(__name__)

    def dispatch(self, text: str) -> str:
        if len(text) > _MAX_MESSAGE_LENGTH:
            return ""
        tokens = text.strip().split()
        if not tokens or not tokens[0].startswith("/"):
            return ""
        name, args = tokens[0].lower(), tokens[1:]
        cmd = self._commands.get(name)
        if cmd is None:
            return "❓ Unknown command, use /help"
        if len(args) != cmd.arg_count:
            return f"❓ Usage: {cmd.usage}"
        self._logger.info(f"Executing {name} with args {args}")
        return cmd.execute(args)
