from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from decimal import Decimal, InvalidOperation
from pathlib import Path

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
            result = self._find_config(symbol)
            if result is None:
                return f"{symbol} is not tracked"
            _, config = result
            for sc in config.symbols:
                if sc.symbol == symbol:
                    if not sc.prices:
                        return f"{symbol} targets: none"
                    prices_str = ", ".join(str(p) for p in sc.prices)
                    return f"{symbol} targets: {prices_str}"
            return f"{symbol} is not tracked"
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
            result = self._find_config(symbol)
            if result is None:
                return f"{symbol} is not tracked"
            path, config = result
            updated_symbols = []
            for sc in config.symbols:
                if sc.symbol == symbol:
                    if price in sc.prices:
                        return f"{symbol} already has target {price}"
                    updated_symbols.append(
                        SymbolConfig(symbol=sc.symbol, prices=sc.prices + [price])
                    )
                else:
                    updated_symbols.append(sc)
            new_config = MonitorStocksConfig(interval=config.interval, symbols=updated_symbols)
            ConfigManager(path).write_monitor_stocks_config(new_config)
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
            result = self._find_config(symbol)
            if result is None:
                return f"{symbol} is not tracked"
            path, config = result
            updated_symbols = []
            found = False
            for sc in config.symbols:
                if sc.symbol == symbol:
                    if price not in sc.prices:
                        return f"{symbol} does not have target {price}"
                    updated_symbols.append(
                        SymbolConfig(
                            symbol=sc.symbol,
                            prices=[p for p in sc.prices if p != price],
                        )
                    )
                    found = True
                else:
                    updated_symbols.append(sc)
            if not found:
                return f"{symbol} is not tracked"
            new_config = MonitorStocksConfig(interval=config.interval, symbols=updated_symbols)
            ConfigManager(path).write_monitor_stocks_config(new_config)
            return f"Removed target {price} from {symbol}"
        except Exception as e:
            return f"Error: {e}"


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
    def __init__(self, commands: list[BotCommand]) -> None:
        self._commands = {cmd.name: cmd for cmd in commands}

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
        return cmd.execute(args)
