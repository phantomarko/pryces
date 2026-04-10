from decimal import Decimal
from unittest.mock import Mock

from pryces.application.dtos import StockStatisticsDTO
from pryces.application.interfaces import StockStatisticsProvider
from pryces.application.use_cases.get_stocks_statistics import (
    GetStocksStatistics,
    GetStocksStatisticsRequest,
)
from pryces.domain.stock_statistics import HistoricalClose, StatisticsPeriod, StockStatistics
from pryces.domain.stocks import Currency


class TestGetStocksStatistics:

    def setup_method(self):
        self.mock_provider = Mock(spec=StockStatisticsProvider)

    def test_handle_returns_empty_list_for_empty_input(self):
        self.mock_provider.get_stock_statistics.return_value = []
        request = GetStocksStatisticsRequest(symbols=[])
        use_case = GetStocksStatistics(provider=self.mock_provider)

        result = use_case.handle(request)

        assert result == []
        self.mock_provider.get_stock_statistics.assert_called_once_with([])

    def test_handle_returns_dto_for_single_symbol(self):
        self.mock_provider.get_stock_statistics.return_value = [
            StockStatistics(
                symbol="AAPL",
                current_price=Decimal("150"),
                historical_closes=[],
            )
        ]
        request = GetStocksStatisticsRequest(symbols=["AAPL"])
        use_case = GetStocksStatistics(provider=self.mock_provider)

        result = use_case.handle(request)

        assert len(result) == 1
        assert isinstance(result[0], StockStatisticsDTO)
        assert result[0].symbol == "AAPL"
        assert result[0].current_price == Decimal("150")

    def test_handle_preserves_order_for_multiple_symbols(self):
        self.mock_provider.get_stock_statistics.return_value = [
            StockStatistics(symbol="AAPL", current_price=Decimal("150"), historical_closes=[]),
            StockStatistics(symbol="GOOGL", current_price=Decimal("170"), historical_closes=[]),
            StockStatistics(symbol="MSFT", current_price=Decimal("400"), historical_closes=[]),
        ]
        request = GetStocksStatisticsRequest(symbols=["AAPL", "GOOGL", "MSFT"])
        use_case = GetStocksStatistics(provider=self.mock_provider)

        result = use_case.handle(request)

        assert len(result) == 3
        assert result[0].symbol == "AAPL"
        assert result[1].symbol == "GOOGL"
        assert result[2].symbol == "MSFT"

    def test_handle_maps_currency_to_string(self):
        self.mock_provider.get_stock_statistics.return_value = [
            StockStatistics(
                symbol="AAPL",
                current_price=Decimal("150"),
                historical_closes=[],
                currency=Currency.USD,
            )
        ]
        request = GetStocksStatisticsRequest(symbols=["AAPL"])
        use_case = GetStocksStatistics(provider=self.mock_provider)

        result = use_case.handle(request)

        assert result[0].currency == "USD"

    def test_handle_maps_none_currency(self):
        self.mock_provider.get_stock_statistics.return_value = [
            StockStatistics(
                symbol="AAPL",
                current_price=Decimal("150"),
                historical_closes=[],
                currency=None,
            )
        ]
        request = GetStocksStatisticsRequest(symbols=["AAPL"])
        use_case = GetStocksStatistics(provider=self.mock_provider)

        result = use_case.handle(request)

        assert result[0].currency is None

    def test_handle_maps_price_changes(self):
        self.mock_provider.get_stock_statistics.return_value = [
            StockStatistics(
                symbol="AAPL",
                current_price=Decimal("150"),
                historical_closes=[
                    HistoricalClose(StatisticsPeriod.ONE_DAY, Decimal("140")),
                    HistoricalClose(StatisticsPeriod.ONE_YEAR, Decimal("100")),
                ],
            )
        ]
        request = GetStocksStatisticsRequest(symbols=["AAPL"])
        use_case = GetStocksStatistics(provider=self.mock_provider)

        result = use_case.handle(request)

        price_changes = result[0].price_changes
        assert len(price_changes) == 2
        assert price_changes[0].period == "1D"
        assert price_changes[0].close_price == Decimal("140")
        assert price_changes[0].change == Decimal("10")
        assert price_changes[1].period == "1Y"
        assert price_changes[1].change == Decimal("50")

    def test_handle_passes_symbols_to_provider(self):
        self.mock_provider.get_stock_statistics.return_value = []
        request = GetStocksStatisticsRequest(symbols=["AAPL", "TSLA"])
        use_case = GetStocksStatistics(provider=self.mock_provider)

        use_case.handle(request)

        self.mock_provider.get_stock_statistics.assert_called_once_with(["AAPL", "TSLA"])
