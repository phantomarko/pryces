from decimal import Decimal

import pytest

from pryces.presentation.scripts.config import MonitorStocksConfig, SymbolConfig


def make_symbol(symbol: str = "AAPL", prices: list = None) -> SymbolConfig:
    return SymbolConfig(symbol=symbol, prices=prices or [Decimal("5")])


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
