import pytest

from pryces.presentation.scripts.monitor_stocks import MonitorStocksConfig


class TestMonitorStocksConfig:

    def test_valid_config(self):
        config = MonitorStocksConfig(iterations=2, interval=5, symbols=["AAPL", "GOOGL"])

        assert config.iterations == 2
        assert config.interval == 5
        assert config.symbols == ["AAPL", "GOOGL"]

    def test_zero_iterations_raises_value_error(self):
        with pytest.raises(ValueError, match="iterations must be a positive integer"):
            MonitorStocksConfig(iterations=0, interval=5, symbols=["AAPL"])

    def test_negative_iterations_raises_value_error(self):
        with pytest.raises(ValueError, match="iterations must be a positive integer"):
            MonitorStocksConfig(iterations=-1, interval=5, symbols=["AAPL"])

    def test_zero_interval_raises_value_error(self):
        with pytest.raises(ValueError, match="interval must be a positive integer"):
            MonitorStocksConfig(iterations=1, interval=0, symbols=["AAPL"])

    def test_negative_interval_raises_value_error(self):
        with pytest.raises(ValueError, match="interval must be a positive integer"):
            MonitorStocksConfig(iterations=1, interval=-5, symbols=["AAPL"])

    def test_empty_symbols_raises_value_error(self):
        with pytest.raises(ValueError, match="symbols must be a non-empty list"):
            MonitorStocksConfig(iterations=1, interval=5, symbols=[])

    def test_non_integer_iterations_raises_value_error(self):
        with pytest.raises(ValueError, match="iterations must be a positive integer"):
            MonitorStocksConfig(iterations="2", interval=5, symbols=["AAPL"])

    def test_non_integer_interval_raises_value_error(self):
        with pytest.raises(ValueError, match="interval must be a positive integer"):
            MonitorStocksConfig(iterations=1, interval="5", symbols=["AAPL"])

    def test_non_list_symbols_raises_value_error(self):
        with pytest.raises(ValueError, match="symbols must be a non-empty list"):
            MonitorStocksConfig(iterations=1, interval=5, symbols="AAPL")
