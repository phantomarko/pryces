from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from decimal import Decimal, InvalidOperation
from pathlib import Path

from ...application.interfaces import LoggerFactory
from .config import ConfigManager, MonitorStocksConfig, SymbolConfig


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
_GetAllSymbolsFn = Callable[[], list[str]]
_GetConfigNamesFn = Callable[[], list[str]]


def _find_symbol_config(
    find_config: _FindConfigFn, symbol: str
) -> tuple[Path, MonitorStocksConfig, SymbolConfig] | str:
    result = find_config(symbol)
    if result is None:
        return f"{symbol} is not tracked"
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
                return f"{symbol} targets: none"
            prices_str = ", ".join(str(p) for p in sc.prices)
            return f"{symbol} targets: {prices_str}"
        except Exception as e:
            return f"Error: {e}"


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
        try:
            price = Decimal(args[1])
        except InvalidOperation:
            return f"Invalid price: {args[1]}"

        try:
            result = _find_symbol_config(self._find_config, symbol)
            if isinstance(result, str):
                return result
            path, config, sc = result
            if price in sc.prices:
                return f"{symbol} already has target {price}"
            _update_symbol_prices(path, config, symbol, sc.prices + [price])
            return f"Added target {price} to {symbol}"
        except Exception as e:
            return f"Error: {e}"


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
        try:
            price = Decimal(args[1])
        except InvalidOperation:
            return f"Invalid price: {args[1]}"

        try:
            result = _find_symbol_config(self._find_config, symbol)
            if isinstance(result, str):
                return result
            path, config, sc = result
            if price not in sc.prices:
                return f"{symbol} does not have target {price}"
            _update_symbol_prices(path, config, symbol, [p for p in sc.prices if p != price])
            return f"Removed target {price} from {symbol}"
        except Exception as e:
            return f"Error: {e}"


class SymbolsCommand(BotCommand):
    def __init__(self, get_all_symbols: _GetAllSymbolsFn) -> None:
        self._get_all_symbols = get_all_symbols

    @property
    def name(self) -> str:
        return "/symbols"

    @property
    def usage(self) -> str:
        return "/symbols"

    @property
    def description(self) -> str:
        return "List all tracked symbols"

    @property
    def arg_count(self) -> int:
        return 0

    def execute(self, args: list[str]) -> str:
        symbols = self._get_all_symbols()
        if not symbols:
            return "No symbols tracked"
        return ", ".join(symbols)


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
            return "No configs found"
        return ", ".join(names)


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
        lines = [f"{cmd.usage} — {cmd.description}" for cmd in self._commands]
        return "\n".join(lines)


class BotCommandDispatcher:
    def __init__(self, commands: list[BotCommand], logger_factory: LoggerFactory) -> None:
        self._commands = {cmd.name: cmd for cmd in commands}
        self._logger = logger_factory.get_logger(__name__)

    def dispatch(self, text: str) -> str:
        tokens = text.strip().split()
        if not tokens or not tokens[0].startswith("/"):
            return ""
        name, args = tokens[0].lower(), tokens[1:]
        cmd = self._commands.get(name)
        if cmd is None:
            return "Unknown command, use /help"
        if len(args) != cmd.arg_count:
            return f"Usage: {cmd.usage}"
        self._logger.info(f"Executing {name} with args {args}")
        return cmd.execute(args)
