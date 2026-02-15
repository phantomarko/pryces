import pytest

from pryces.presentation.scripts.monitor_stocks import MonitorStocksConfig


class TestMonitorStocksConfig:

    def test_valid_config(self):
        config = MonitorStocksConfig(duration=2, interval=5, symbols=["AAPL", "GOOGL"])

        assert config.duration == 2
        assert config.interval == 5
        assert config.symbols == ["AAPL", "GOOGL"]

    def test_zero_duration_raises_value_error(self):
        with pytest.raises(ValueError, match="duration must be a positive integer"):
            MonitorStocksConfig(duration=0, interval=5, symbols=["AAPL"])

    def test_negative_duration_raises_value_error(self):
        with pytest.raises(ValueError, match="duration must be a positive integer"):
            MonitorStocksConfig(duration=-1, interval=5, symbols=["AAPL"])

    def test_zero_interval_raises_value_error(self):
        with pytest.raises(ValueError, match="interval must be a positive integer"):
            MonitorStocksConfig(duration=1, interval=0, symbols=["AAPL"])

    def test_negative_interval_raises_value_error(self):
        with pytest.raises(ValueError, match="interval must be a positive integer"):
            MonitorStocksConfig(duration=1, interval=-5, symbols=["AAPL"])

    def test_empty_symbols_raises_value_error(self):
        with pytest.raises(ValueError, match="symbols must be a non-empty list"):
            MonitorStocksConfig(duration=1, interval=5, symbols=[])

    def test_non_integer_duration_raises_value_error(self):
        with pytest.raises(ValueError, match="duration must be a positive integer"):
            MonitorStocksConfig(duration="2", interval=5, symbols=["AAPL"])

    def test_non_integer_interval_raises_value_error(self):
        with pytest.raises(ValueError, match="interval must be a positive integer"):
            MonitorStocksConfig(duration=1, interval="5", symbols=["AAPL"])

    def test_non_list_symbols_raises_value_error(self):
        with pytest.raises(ValueError, match="symbols must be a non-empty list"):
            MonitorStocksConfig(duration=1, interval=5, symbols="AAPL")
