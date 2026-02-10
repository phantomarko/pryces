from decimal import Decimal
from unittest.mock import Mock

import pytest

from pryces.application.dtos import StockDTO
from pryces.application.exceptions import StockNotFound
from pryces.application.interfaces import StockProvider
from pryces.application.use_cases.get_stock_price import (
    GetStockPrice,
    GetStockPriceRequest,
)
from pryces.domain.stocks import Stock
from tests.fixtures.factories import create_stock


class TestGetStockPrice:
    def setup_method(self):
        self.mock_provider = Mock(spec=StockProvider)

    def test_handle_returns_stock_price_dto_from_provider(self):
        symbol = "AAPL"
        provider_response = create_stock(
            symbol,
            Decimal("150.25"),
            name="Apple Inc.",
            previousClosePrice=Decimal("148.50"),
            openPrice=Decimal("149.00"),
            dayHigh=Decimal("151.00"),
            dayLow=Decimal("148.00"),
            fiftyDayAverage=Decimal("145.50"),
            twoHundredDayAverage=Decimal("140.00"),
            fiftyTwoWeekHigh=Decimal("180.00"),
            fiftyTwoWeekLow=Decimal("120.00"),
        )
        self.mock_provider.get_stock.return_value = provider_response

        use_case = GetStockPrice(provider=self.mock_provider)
        request = GetStockPriceRequest(symbol=symbol)

        result = use_case.handle(request)

        assert isinstance(result, StockDTO)
        assert result.symbol == provider_response.symbol
        assert result.currentPrice == provider_response.currentPrice
        assert result.name == provider_response.name
        assert result.dayHigh == provider_response.dayHigh
        self.mock_provider.get_stock.assert_called_once_with(symbol)

    def test_handle_raises_stock_not_found_when_provider_returns_none(self):
        symbol = "INVALID"
        self.mock_provider.get_stock.return_value = None

        use_case = GetStockPrice(provider=self.mock_provider)
        request = GetStockPriceRequest(symbol=symbol)

        with pytest.raises(StockNotFound) as exc_info:
            use_case.handle(request)

        assert exc_info.value.symbol == symbol
        assert str(exc_info.value) == f"Stock not found: {symbol}"
        self.mock_provider.get_stock.assert_called_once_with(symbol)

    def test_handle_returns_dto_with_minimal_fields(self):
        symbol = "AAPL"
        minimal_response = Stock(symbol=symbol, currentPrice=Decimal("150.25"))
        self.mock_provider.get_stock.return_value = minimal_response

        use_case = GetStockPrice(provider=self.mock_provider)
        request = GetStockPriceRequest(symbol=symbol)

        result = use_case.handle(request)

        assert isinstance(result, StockDTO)
        assert result.symbol == symbol
        assert result.currentPrice == Decimal("150.25")
        assert result.name is None
        assert result.currency is None
        self.mock_provider.get_stock.assert_called_once_with(symbol)
