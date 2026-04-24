from decimal import Decimal
from unittest.mock import Mock

from pryces.application.interfaces import StockStatisticsProvider
from pryces.application.use_cases.get_stocks_statistics import (
    GetStocksStatistics,
    GetStocksStatisticsRequest,
)
from pryces.domain.stock_statistics import (
    HistoricalClose,
    StatisticsPeriod,
    StockStatistics,
    StockStatisticsFormatter,
)


def _make_stats(symbol: str = "AAPL", current_price: str = "150") -> StockStatistics:
    return StockStatistics(
        symbol=symbol, current_price=Decimal(current_price), historical_closes=[]
    )


def _make_use_case(provider, formatter=None) -> GetStocksStatistics:
    if formatter is None:
        formatter = Mock(spec=StockStatisticsFormatter)
        formatter.format.return_value = "formatted"
    return GetStocksStatistics(provider=provider, formatter=formatter)


class TestGetStocksStatistics:

    def setup_method(self):
        self.mock_provider = Mock(spec=StockStatisticsProvider)
        self.mock_formatter = Mock(spec=StockStatisticsFormatter)
        self.mock_formatter.format.return_value = "formatted"

    def test_handle_returns_empty_list_for_empty_input(self):
        self.mock_provider.get_stock_statistics.return_value = []
        request = GetStocksStatisticsRequest(symbols=[])
        use_case = GetStocksStatistics(provider=self.mock_provider, formatter=self.mock_formatter)

        result = use_case.handle(request)

        assert result == []
        self.mock_provider.get_stock_statistics.assert_called_once_with([])

    def test_handle_returns_formatted_string_for_single_symbol(self):
        self.mock_provider.get_stock_statistics.return_value = [_make_stats("AAPL")]
        self.mock_formatter.format.return_value = "📊 AAPL — 150.00"
        request = GetStocksStatisticsRequest(symbols=["AAPL"])
        use_case = GetStocksStatistics(provider=self.mock_provider, formatter=self.mock_formatter)

        result = use_case.handle(request)

        assert len(result) == 1
        assert isinstance(result[0], str)
        assert result[0] == "📊 AAPL — 150.00"

    def test_handle_preserves_order_for_multiple_symbols(self):
        stats = [_make_stats("AAPL"), _make_stats("GOOGL"), _make_stats("MSFT")]
        self.mock_provider.get_stock_statistics.return_value = stats
        self.mock_formatter.format.side_effect = ["📊 AAPL", "📊 GOOGL", "📊 MSFT"]
        request = GetStocksStatisticsRequest(symbols=["AAPL", "GOOGL", "MSFT"])
        use_case = GetStocksStatistics(provider=self.mock_provider, formatter=self.mock_formatter)

        result = use_case.handle(request)

        assert result == ["📊 AAPL", "📊 GOOGL", "📊 MSFT"]

    def test_handle_calls_formatter_for_each_stats(self):
        stats = [_make_stats("AAPL"), _make_stats("TSLA")]
        self.mock_provider.get_stock_statistics.return_value = stats
        request = GetStocksStatisticsRequest(symbols=["AAPL", "TSLA"])
        use_case = GetStocksStatistics(provider=self.mock_provider, formatter=self.mock_formatter)

        use_case.handle(request)

        assert self.mock_formatter.format.call_count == 2
        self.mock_formatter.format.assert_any_call(stats[0])
        self.mock_formatter.format.assert_any_call(stats[1])

    def test_handle_passes_symbols_to_provider(self):
        self.mock_provider.get_stock_statistics.return_value = []
        request = GetStocksStatisticsRequest(symbols=["AAPL", "TSLA"])
        use_case = GetStocksStatistics(provider=self.mock_provider, formatter=self.mock_formatter)

        use_case.handle(request)

        self.mock_provider.get_stock_statistics.assert_called_once_with(["AAPL", "TSLA"])
