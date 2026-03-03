import logging
from decimal import Decimal
from unittest.mock import Mock

import pytest

from pryces.application.dtos import TargetPriceDTO
from pryces.application.use_cases.trigger_stocks_notifications import TriggerStocksNotifications
from pryces.presentation.scripts.config import (
    ConfigManager,
    ConfigRefresher,
    MonitorStocksConfig,
    SymbolConfig,
)
from pryces.presentation.scripts.monitor_stocks import MonitorStocksScript


def make_symbol(symbol: str = "AAPL", prices: list = None) -> SymbolConfig:
    return SymbolConfig(symbol=symbol, prices=prices or [Decimal("5")])


def make_config(**overrides) -> MonitorStocksConfig:
    defaults = {
        "interval": 5,
        "symbols": [
            SymbolConfig("AAPL", [Decimal("150"), Decimal("200")]),
            SymbolConfig("GOOGL", [Decimal("100")]),
        ],
    }
    defaults.update(overrides)
    return MonitorStocksConfig(**defaults)


def make_refresher(config=None, config_manager=None) -> ConfigRefresher:
    if config is None:
        config = make_config()
    if config_manager is None:
        config_manager = Mock(spec=ConfigManager)
    return ConfigRefresher(config_manager=config_manager, config=config)


class TestConfigRefresherRemoveFulfilledTargets:

    def setup_method(self):
        self.mock_config_manager = Mock(spec=ConfigManager)
        self.config = make_config()
        self.refresher = ConfigRefresher(
            config_manager=self.mock_config_manager, config=self.config
        )

    def test_does_nothing_when_fulfilled_is_empty(self):
        self.refresher.remove_fulfilled_targets([])

        self.mock_config_manager.write_monitor_stocks_config.assert_not_called()

    def test_does_nothing_when_no_prices_match(self):
        self.refresher.remove_fulfilled_targets(
            [TargetPriceDTO(symbol="AAPL", target=Decimal("999"))]
        )

        self.mock_config_manager.write_monitor_stocks_config.assert_not_called()

    def test_removes_fulfilled_price_from_symbol(self):
        self.refresher.remove_fulfilled_targets(
            [TargetPriceDTO(symbol="AAPL", target=Decimal("150"))]
        )

        expected = make_config(
            symbols=[
                SymbolConfig("AAPL", [Decimal("200")]),
                SymbolConfig("GOOGL", [Decimal("100")]),
            ]
        )
        self.mock_config_manager.write_monitor_stocks_config.assert_called_once_with(expected)

    def test_keeps_symbol_with_empty_prices_when_all_its_prices_are_fulfilled(self):
        self.refresher.remove_fulfilled_targets(
            [TargetPriceDTO(symbol="GOOGL", target=Decimal("100"))]
        )

        expected = make_config(
            symbols=[
                SymbolConfig("AAPL", [Decimal("150"), Decimal("200")]),
                SymbolConfig("GOOGL", []),
            ]
        )
        self.mock_config_manager.write_monitor_stocks_config.assert_called_once_with(expected)

    def test_writes_config_with_all_symbols_emptied_when_all_prices_fulfilled(self):
        self.refresher.remove_fulfilled_targets(
            [
                TargetPriceDTO(symbol="AAPL", target=Decimal("150")),
                TargetPriceDTO(symbol="AAPL", target=Decimal("200")),
                TargetPriceDTO(symbol="GOOGL", target=Decimal("100")),
            ]
        )

        expected = make_config(
            symbols=[
                SymbolConfig("AAPL", []),
                SymbolConfig("GOOGL", []),
            ]
        )
        self.mock_config_manager.write_monitor_stocks_config.assert_called_once_with(expected)

    def test_updates_config_after_write(self):
        self.refresher.remove_fulfilled_targets(
            [TargetPriceDTO(symbol="AAPL", target=Decimal("150"))]
        )

        assert self.refresher.config == make_config(
            symbols=[
                SymbolConfig("AAPL", [Decimal("200")]),
                SymbolConfig("GOOGL", [Decimal("100")]),
            ]
        )


class TestConfigRefresherRefresh:

    def test_updates_config_when_disk_config_differs(self):
        mock_manager = Mock(spec=ConfigManager)
        original = make_config()
        new_config = make_config(interval=10)
        mock_manager.read_monitor_stocks_config.return_value = new_config
        refresher = ConfigRefresher(config_manager=mock_manager, config=original)

        refresher.refresh()

        assert refresher.config == new_config

    def test_does_nothing_when_config_unchanged(self):
        mock_manager = Mock(spec=ConfigManager)
        config = make_config()
        mock_manager.read_monitor_stocks_config.return_value = config
        refresher = ConfigRefresher(config_manager=mock_manager, config=config)

        refresher.refresh()

        assert refresher.config == config

    def test_silently_ignores_read_errors(self):
        mock_manager = Mock(spec=ConfigManager)
        original = make_config()
        mock_manager.read_monitor_stocks_config.side_effect = Exception("disk error")
        refresher = ConfigRefresher(config_manager=mock_manager, config=original)

        refresher.refresh()

        assert refresher.config == original


class TestConfigRefresherLogConfig:

    def test_logs_monitoring_cadence_and_symbols(self, caplog):
        config = make_config()
        refresher = make_refresher(config=config)

        with caplog.at_level(logging.INFO):
            refresher.log_config()

        assert "Monitoring every 5s." in caplog.text
        assert "AAPL @ 150, 200" in caplog.text
        assert "GOOGL @ 100" in caplog.text


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
        config = MonitorStocksConfig(interval=5, symbols=symbols)

        assert config.interval == 5
        assert config.symbols == symbols

    def test_zero_interval_raises_value_error(self):
        with pytest.raises(ValueError, match="interval must be a positive integer"):
            MonitorStocksConfig(interval=0, symbols=[make_symbol()])

    def test_negative_interval_raises_value_error(self):
        with pytest.raises(ValueError, match="interval must be a positive integer"):
            MonitorStocksConfig(interval=-5, symbols=[make_symbol()])

    def test_empty_symbols_raises_value_error(self):
        with pytest.raises(ValueError, match="symbols must be a non-empty list"):
            MonitorStocksConfig(interval=5, symbols=[])

    def test_non_integer_interval_raises_value_error(self):
        with pytest.raises(ValueError, match="interval must be a positive integer"):
            MonitorStocksConfig(interval="5", symbols=[make_symbol()])

    def test_non_list_symbols_raises_value_error(self):
        with pytest.raises(ValueError, match="symbols must be a non-empty list"):
            MonitorStocksConfig(interval=5, symbols="AAPL")
