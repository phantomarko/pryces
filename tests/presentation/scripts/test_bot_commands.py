import json
from decimal import Decimal
from unittest.mock import Mock

import pytest

from pryces.presentation.scripts.bot_commands import (
    BotCommandDispatcher,
    ConfigsCommand,
    HelpCommand,
    SymbolsCommand,
    TargetAddCommand,
    TargetRemoveCommand,
    TargetsCommand,
)
from pryces.presentation.scripts.config import MonitorStocksConfig, SymbolConfig


def make_config(**overrides) -> MonitorStocksConfig:
    defaults = {
        "interval": 30,
        "symbols": [
            SymbolConfig("AAPL", [Decimal("150"), Decimal("200")]),
            SymbolConfig("GOOGL", [Decimal("100")]),
        ],
    }
    defaults.update(overrides)
    return MonitorStocksConfig(**defaults)


def write_config(tmp_path, config, name="test.json"):
    config_data = {
        "interval": config.interval,
        "symbols": [
            {"symbol": s.symbol, "prices": [float(p) for p in s.prices]} for s in config.symbols
        ],
    }
    path = tmp_path / name
    path.write_text(json.dumps(config_data))
    return path


def make_find_config(tmp_path, config=None, name="test.json"):
    if config is None:
        config = make_config()
    path = write_config(tmp_path, config, name)

    def find_config(symbol):
        for sc in config.symbols:
            if sc.symbol == symbol.upper():
                from pryces.presentation.scripts.config import ConfigManager

                return path, ConfigManager(path).read_monitor_stocks_config()
        return None

    return find_config


class TestTargetsCommand:

    def test_lists_targets_for_symbol(self, tmp_path):
        find_config = make_find_config(tmp_path)
        cmd = TargetsCommand(find_config)

        result = cmd.execute(["AAPL"])

        assert "150" in result
        assert "200" in result

    def test_reports_no_targets_when_empty(self, tmp_path):
        config = make_config(
            symbols=[SymbolConfig("AAPL", []), SymbolConfig("GOOGL", [Decimal("100")])]
        )
        find_config = make_find_config(tmp_path, config)
        cmd = TargetsCommand(find_config)

        result = cmd.execute(["AAPL"])

        assert "AAPL targets: none" == result

    def test_reports_symbol_not_found(self, tmp_path):
        find_config = make_find_config(tmp_path)
        cmd = TargetsCommand(find_config)

        result = cmd.execute(["MSFT"])

        assert "is not tracked" in result

    def test_uppercases_symbol(self, tmp_path):
        find_config = make_find_config(tmp_path)
        cmd = TargetsCommand(find_config)

        result = cmd.execute(["aapl"])

        assert "150" in result


class TestTargetAddCommand:

    def test_adds_target_price(self, tmp_path):
        find_config = make_find_config(tmp_path)
        cmd = TargetAddCommand(find_config)

        result = cmd.execute(["AAPL", "250"])

        assert "Added" in result
        assert "250" in result

    def test_persists_added_target(self, tmp_path):
        find_config = make_find_config(tmp_path)
        cmd = TargetAddCommand(find_config)

        cmd.execute(["AAPL", "250"])

        saved = json.loads((tmp_path / "test.json").read_text())
        aapl = next(s for s in saved["symbols"] if s["symbol"] == "AAPL")
        assert 250.0 in aapl["prices"]

    def test_rejects_duplicate_target(self, tmp_path):
        find_config = make_find_config(tmp_path)
        cmd = TargetAddCommand(find_config)

        result = cmd.execute(["AAPL", "150"])

        assert "already has" in result

    def test_rejects_invalid_price(self, tmp_path):
        find_config = make_find_config(tmp_path)
        cmd = TargetAddCommand(find_config)

        result = cmd.execute(["AAPL", "abc"])

        assert "Invalid price" in result

    def test_reports_symbol_not_found(self, tmp_path):
        find_config = make_find_config(tmp_path)
        cmd = TargetAddCommand(find_config)

        result = cmd.execute(["MSFT", "100"])

        assert "is not tracked" in result


class TestTargetRemoveCommand:

    def test_removes_target_price(self, tmp_path):
        find_config = make_find_config(tmp_path)
        cmd = TargetRemoveCommand(find_config)

        result = cmd.execute(["AAPL", "150"])

        assert "Removed" in result
        assert "150" in result

    def test_persists_removed_target(self, tmp_path):
        find_config = make_find_config(tmp_path)
        cmd = TargetRemoveCommand(find_config)

        cmd.execute(["AAPL", "150"])

        saved = json.loads((tmp_path / "test.json").read_text())
        aapl = next(s for s in saved["symbols"] if s["symbol"] == "AAPL")
        assert 150.0 not in aapl["prices"]
        assert 200.0 in aapl["prices"]

    def test_reports_target_not_present(self, tmp_path):
        find_config = make_find_config(tmp_path)
        cmd = TargetRemoveCommand(find_config)

        result = cmd.execute(["AAPL", "999"])

        assert "does not have" in result

    def test_rejects_invalid_price(self, tmp_path):
        find_config = make_find_config(tmp_path)
        cmd = TargetRemoveCommand(find_config)

        result = cmd.execute(["AAPL", "abc"])

        assert "Invalid price" in result

    def test_reports_symbol_not_found(self, tmp_path):
        find_config = make_find_config(tmp_path)
        cmd = TargetRemoveCommand(find_config)

        result = cmd.execute(["MSFT", "100"])

        assert "is not tracked" in result


class TestSymbolsCommand:

    def test_lists_all_symbols(self):
        cmd = SymbolsCommand(lambda: ["AAPL", "GOOGL", "MSFT"])

        result = cmd.execute([])

        assert result == "AAPL, GOOGL, MSFT"

    def test_returns_no_symbols_message_when_empty(self):
        cmd = SymbolsCommand(lambda: [])

        result = cmd.execute([])

        assert result == "No symbols tracked"


class TestConfigsCommand:

    def test_lists_config_names(self):
        cmd = ConfigsCommand(lambda: ["alpha", "beta"])
        result = cmd.execute([])
        assert result == "alpha, beta"

    def test_returns_no_configs_message_when_empty(self):
        cmd = ConfigsCommand(lambda: [])
        result = cmd.execute([])
        assert result == "No configs found"


class TestHelpCommand:

    def test_lists_all_commands(self):
        targets = TargetsCommand(lambda s: None)
        add = TargetAddCommand(lambda s: None)
        help_cmd = HelpCommand([targets, add])

        result = help_cmd.execute([])

        assert "/targets" in result
        assert "/target_add" in result
        assert "List all target" in result
        assert "Add a target" in result


class TestBotCommandDispatcher:

    def _make_dispatcher(self):
        targets = TargetsCommand(lambda s: None)
        help_cmd = HelpCommand([targets])
        return BotCommandDispatcher([targets, help_cmd], logger_factory=Mock())

    def test_dispatches_known_command(self):
        dispatcher = self._make_dispatcher()

        result = dispatcher.dispatch("/help")

        assert "/targets" in result

    def test_returns_unknown_command_message(self):
        dispatcher = self._make_dispatcher()

        result = dispatcher.dispatch("/unknown")

        assert "Unknown command" in result

    def test_returns_usage_on_wrong_arg_count(self):
        dispatcher = self._make_dispatcher()

        result = dispatcher.dispatch("/targets")

        assert "Usage:" in result
        assert "/targets <symbol>" in result

    def test_returns_empty_string_for_non_command_text(self):
        dispatcher = self._make_dispatcher()

        result = dispatcher.dispatch("hello world")

        assert result == ""

    def test_returns_empty_string_for_empty_text(self):
        dispatcher = self._make_dispatcher()

        result = dispatcher.dispatch("")

        assert result == ""

    def test_lowercases_command_name(self):
        dispatcher = self._make_dispatcher()

        result = dispatcher.dispatch("/HELP")

        assert "/targets" in result
