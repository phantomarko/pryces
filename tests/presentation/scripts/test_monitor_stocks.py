from decimal import Decimal
from unittest.mock import Mock

import pytest

from pryces.application.dtos import TargetPriceDTO
from pryces.application.use_cases.sync_target_prices import SyncTargetPrices
from pryces.application.use_cases.trigger_stocks_notifications import TriggerStocksNotifications
from pryces.presentation.scripts.config import ConfigManager, MonitorStocksConfig, SymbolConfig
from pryces.presentation.scripts.monitor_stocks import MonitorStocksScript


def make_symbol(symbol: str = "AAPL", prices: list = None) -> SymbolConfig:
    return SymbolConfig(symbol=symbol, prices=prices or [Decimal("5")])


class TestMonitorStocksScriptWriteConfig:

    def setup_method(self):
        self.mock_trigger = Mock(spec=TriggerStocksNotifications)
        self.mock_sync = Mock(spec=SyncTargetPrices)
        self.mock_config_manager = Mock(spec=ConfigManager)
        self.config = MonitorStocksConfig(
            duration=1,
            interval=5,
            symbols=[
                SymbolConfig("AAPL", [Decimal("150"), Decimal("200")]),
                SymbolConfig("GOOGL", [Decimal("100")]),
            ],
        )
        self.mock_config_manager.read_monitor_stocks_config.return_value = self.config
        self.script = MonitorStocksScript(
            trigger_notifications=self.mock_trigger,
            sync_target_prices=self.mock_sync,
            config_manager=self.mock_config_manager,
        )

    def test_does_nothing_when_fulfilled_is_empty(self):
        self.script._write_config([])

        self.mock_config_manager.write_monitor_stocks_config.assert_not_called()

    def test_does_nothing_when_no_prices_match(self):
        self.script._write_config([TargetPriceDTO(symbol="AAPL", target=Decimal("999"))])

        self.mock_config_manager.write_monitor_stocks_config.assert_not_called()

    def test_removes_fulfilled_price_from_symbol(self):
        self.script._write_config([TargetPriceDTO(symbol="AAPL", target=Decimal("150"))])

        expected = MonitorStocksConfig(
            duration=1,
            interval=5,
            symbols=[
                SymbolConfig("AAPL", [Decimal("200")]),
                SymbolConfig("GOOGL", [Decimal("100")]),
            ],
        )
        self.mock_config_manager.write_monitor_stocks_config.assert_called_once_with(expected)

    def test_keeps_symbol_with_empty_prices_when_all_its_prices_are_fulfilled(self):
        self.script._write_config([TargetPriceDTO(symbol="GOOGL", target=Decimal("100"))])

        expected = MonitorStocksConfig(
            duration=1,
            interval=5,
            symbols=[
                SymbolConfig("AAPL", [Decimal("150"), Decimal("200")]),
                SymbolConfig("GOOGL", []),
            ],
        )
        self.mock_config_manager.write_monitor_stocks_config.assert_called_once_with(expected)

    def test_writes_config_with_all_symbols_emptied_when_all_prices_fulfilled(self):
        self.script._write_config(
            [
                TargetPriceDTO(symbol="AAPL", target=Decimal("150")),
                TargetPriceDTO(symbol="AAPL", target=Decimal("200")),
                TargetPriceDTO(symbol="GOOGL", target=Decimal("100")),
            ]
        )

        expected = MonitorStocksConfig(
            duration=1,
            interval=5,
            symbols=[
                SymbolConfig("AAPL", []),
                SymbolConfig("GOOGL", []),
            ],
        )
        self.mock_config_manager.write_monitor_stocks_config.assert_called_once_with(expected)

    def test_updates_self_config_after_write(self):
        self.script._write_config([TargetPriceDTO(symbol="AAPL", target=Decimal("150"))])

        assert self.script._config == MonitorStocksConfig(
            duration=1,
            interval=5,
            symbols=[
                SymbolConfig("AAPL", [Decimal("200")]),
                SymbolConfig("GOOGL", [Decimal("100")]),
            ],
        )


class TestSymbolConfig:

    def test_valid_symbol_config(self):
        config = SymbolConfig(symbol="AAPL", prices=[Decimal("5"), Decimal("4.5")])

        assert config.symbol == "AAPL"
        assert config.prices == [Decimal("5"), Decimal("4.5")]

    def test_accepts_empty_symbol(self):
        config = SymbolConfig(symbol="", prices=[Decimal("5")])

        assert config.symbol == ""

    def test_accepts_empty_prices(self):
        config = SymbolConfig(symbol="AAPL", prices=[])

        assert config.prices == []


class TestMonitorStocksConfig:

    def test_valid_config(self):
        symbols = [make_symbol("AAPL"), make_symbol("GOOGL")]
        config = MonitorStocksConfig(duration=2, interval=5, symbols=symbols)

        assert config.duration == 2
        assert config.interval == 5
        assert config.symbols == symbols

    def test_zero_duration_raises_value_error(self):
        with pytest.raises(ValueError, match="duration must be a positive integer"):
            MonitorStocksConfig(duration=0, interval=5, symbols=[make_symbol()])

    def test_negative_duration_raises_value_error(self):
        with pytest.raises(ValueError, match="duration must be a positive integer"):
            MonitorStocksConfig(duration=-1, interval=5, symbols=[make_symbol()])

    def test_zero_interval_raises_value_error(self):
        with pytest.raises(ValueError, match="interval must be a positive integer"):
            MonitorStocksConfig(duration=1, interval=0, symbols=[make_symbol()])

    def test_negative_interval_raises_value_error(self):
        with pytest.raises(ValueError, match="interval must be a positive integer"):
            MonitorStocksConfig(duration=1, interval=-5, symbols=[make_symbol()])

    def test_empty_symbols_raises_value_error(self):
        with pytest.raises(ValueError, match="symbols must be a non-empty list"):
            MonitorStocksConfig(duration=1, interval=5, symbols=[])

    def test_non_integer_duration_raises_value_error(self):
        with pytest.raises(ValueError, match="duration must be a positive integer"):
            MonitorStocksConfig(duration="2", interval=5, symbols=[make_symbol()])

    def test_non_integer_interval_raises_value_error(self):
        with pytest.raises(ValueError, match="interval must be a positive integer"):
            MonitorStocksConfig(duration=1, interval="5", symbols=[make_symbol()])

    def test_non_list_symbols_raises_value_error(self):
        with pytest.raises(ValueError, match="symbols must be a non-empty list"):
            MonitorStocksConfig(duration=1, interval=5, symbols="AAPL")
