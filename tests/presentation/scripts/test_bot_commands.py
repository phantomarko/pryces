import json
from decimal import Decimal
from unittest.mock import Mock

import pytest

from pryces.presentation.scripts.bot_commands import (
    _MAX_MESSAGE_LENGTH,
    BotCommandDispatcher,
    ConfigsCommand,
    HelpCommand,
    StatsCommand,
    SymbolAddCommand,
    SymbolRemoveCommand,
    SymbolsCommand,
    TargetAddCommand,
    TargetRemoveCommand,
    TargetsCommand,
)
from pryces.infrastructure.configs import MonitorStocksConfig, SymbolConfig

from tests.presentation.scripts.factories import make_config


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
                from pryces.infrastructure.configs import ConfigManager

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

        assert "🎯 AAPL targets: none" == result

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


def make_find_config_by_name(tmp_path, config=None, name="test"):
    if config is None:
        config = make_config()
    write_config(tmp_path, config, f"{name}.json")

    def find_config_by_name(config_name):
        if config_name != name:
            return None
        from pryces.infrastructure.configs import ConfigManager

        path = tmp_path / f"{config_name}.json"
        return path, ConfigManager(path).read_monitor_stocks_config()

    return find_config_by_name


class TestSymbolAddCommand:

    def test_adds_symbol_to_config(self, tmp_path):
        find_config_by_name = make_find_config_by_name(tmp_path)
        cmd = SymbolAddCommand(find_config_by_name)

        result = cmd.execute(["MSFT", "test"])

        assert "Added" in result
        assert "MSFT" in result

    def test_persists_added_symbol(self, tmp_path):
        find_config_by_name = make_find_config_by_name(tmp_path)
        cmd = SymbolAddCommand(find_config_by_name)

        cmd.execute(["MSFT", "test"])

        saved = json.loads((tmp_path / "test.json").read_text())
        symbols = [s["symbol"] for s in saved["symbols"]]
        assert "MSFT" in symbols

    def test_rejects_unknown_config(self, tmp_path):
        find_config_by_name = make_find_config_by_name(tmp_path)
        cmd = SymbolAddCommand(find_config_by_name)

        result = cmd.execute(["MSFT", "nonexistent"])

        assert "not found" in result

    def test_rejects_duplicate_symbol(self, tmp_path):
        find_config_by_name = make_find_config_by_name(tmp_path)
        cmd = SymbolAddCommand(find_config_by_name)

        result = cmd.execute(["AAPL", "test"])

        assert "already in" in result

    def test_uppercases_symbol(self, tmp_path):
        find_config_by_name = make_find_config_by_name(tmp_path)
        cmd = SymbolAddCommand(find_config_by_name)

        cmd.execute(["msft", "test"])

        saved = json.loads((tmp_path / "test.json").read_text())
        symbols = [s["symbol"] for s in saved["symbols"]]
        assert "MSFT" in symbols


class TestSymbolRemoveCommand:

    def test_removes_symbol_from_config(self, tmp_path):
        find_config = make_find_config(tmp_path)
        cmd = SymbolRemoveCommand(find_config)

        result = cmd.execute(["AAPL"])

        assert "Removed" in result
        assert "AAPL" in result

    def test_persists_removed_symbol(self, tmp_path):
        find_config = make_find_config(tmp_path)
        cmd = SymbolRemoveCommand(find_config)

        cmd.execute(["AAPL"])

        saved = json.loads((tmp_path / "test.json").read_text())
        symbols = [s["symbol"] for s in saved["symbols"]]
        assert "AAPL" not in symbols
        assert "GOOGL" in symbols

    def test_reports_symbol_not_found(self, tmp_path):
        find_config = make_find_config(tmp_path)
        cmd = SymbolRemoveCommand(find_config)

        result = cmd.execute(["MSFT"])

        assert "is not tracked" in result

    def test_rejects_removing_last_symbol(self, tmp_path):
        config = make_config(symbols=[SymbolConfig("AAPL", [Decimal("150")])])
        find_config = make_find_config(tmp_path, config)
        cmd = SymbolRemoveCommand(find_config)

        result = cmd.execute(["AAPL"])

        assert "Cannot remove the last symbol" in result

    def test_uppercases_symbol(self, tmp_path):
        find_config = make_find_config(tmp_path)
        cmd = SymbolRemoveCommand(find_config)

        result = cmd.execute(["aapl"])

        assert "Removed" in result


class TestSymbolsCommand:

    def test_lists_all_symbols_with_targets(self):
        cmd = SymbolsCommand(
            lambda: [
                ("AAPL", [Decimal("150"), Decimal("200.50")]),
                ("GOOGL", []),
                ("MSFT", [Decimal("300")]),
            ]
        )

        result = cmd.execute([])

        assert result == (
            "📋 Symbols & targets:\n" "1) AAPL — 🎯 150, 200.50\n" "2) GOOGL\n" "3) MSFT — 🎯 300"
        )

    def test_returns_no_symbols_message_when_empty(self):
        cmd = SymbolsCommand(lambda: [])

        result = cmd.execute([])

        assert result == "📋 No symbols tracked"


class TestConfigsCommand:

    def test_lists_config_names(self):
        cmd = ConfigsCommand(lambda: ["alpha", "beta"])
        result = cmd.execute([])
        assert result == "🗂️ alpha, beta"

    def test_returns_no_configs_message_when_empty(self):
        cmd = ConfigsCommand(lambda: [])
        result = cmd.execute([])
        assert result == "🗂️ No configs found"


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

    def test_ignores_message_exceeding_max_length(self):
        dispatcher = self._make_dispatcher()

        result = dispatcher.dispatch("/help" + " " * _MAX_MESSAGE_LENGTH)

        assert result == ""

    def test_dispatches_command_at_boundary_length(self):
        dispatcher = self._make_dispatcher()
        text = "/help"
        padding = " " * (_MAX_MESSAGE_LENGTH - len(text))

        result = dispatcher.dispatch(text + padding)

        assert "/targets" in result


class TestTargetAddCommandValidation:

    @pytest.fixture()
    def cmd(self, tmp_path):
        return TargetAddCommand(make_find_config(tmp_path))

    def test_rejects_too_many_integer_digits(self, cmd):
        result = cmd.execute(["AAPL", "12345678"])

        assert result == "❌ Invalid price"

    def test_rejects_too_many_decimal_digits(self, cmd):
        result = cmd.execute(["AAPL", "1.123456789"])

        assert result == "❌ Invalid price"

    def test_accepts_max_integer_digits(self, cmd):
        result = cmd.execute(["AAPL", "1234567"])

        assert "Added" in result

    def test_accepts_max_decimal_digits(self, cmd):
        result = cmd.execute(["AAPL", "1.12345678"])

        assert "Added" in result

    def test_rejects_negative_price(self, cmd):
        result = cmd.execute(["AAPL", "-100"])

        assert result == "❌ Invalid price"

    def test_rejects_zero_price(self, cmd):
        result = cmd.execute(["AAPL", "0"])

        assert result == "❌ Invalid price"

    def test_rejects_scientific_notation(self, cmd):
        result = cmd.execute(["AAPL", "1e5"])

        assert result == "❌ Invalid price"


class TestTargetRemoveCommandValidation:

    @pytest.fixture()
    def cmd(self, tmp_path):
        return TargetRemoveCommand(make_find_config(tmp_path))

    def test_rejects_too_many_integer_digits(self, cmd):
        result = cmd.execute(["AAPL", "12345678"])

        assert result == "❌ Invalid price"

    def test_rejects_negative_price(self, cmd):
        result = cmd.execute(["AAPL", "-100"])

        assert result == "❌ Invalid price"

    def test_rejects_zero_price(self, cmd):
        result = cmd.execute(["AAPL", "0"])

        assert result == "❌ Invalid price"


class TestStatsCommand:
    def test_upcases_symbol_before_passing_to_trigger_function(self):
        received = []
        cmd = StatsCommand(lambda s: received.append(s))

        cmd.execute(["aapl"])

        assert received == ["AAPL"]

    def test_returns_empty_string_on_success(self):
        cmd = StatsCommand(lambda _: None)

        result = cmd.execute(["AAPL"])

        assert result == ""

    def test_returns_error_on_exception(self):
        def raise_error(_):
            raise RuntimeError("network failure")

        cmd = StatsCommand(raise_error)

        result = cmd.execute(["AAPL"])

        assert result.startswith("❌ Error:")
