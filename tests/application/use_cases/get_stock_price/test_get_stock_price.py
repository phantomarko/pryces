"""Unit tests for GetStockPrice use case."""

from decimal import Decimal
from unittest.mock import Mock

import pytest

from pryces.application.providers.dtos import StockPriceResponse
from pryces.application.providers.interfaces import StockPriceProvider
from pryces.application.use_cases.get_stock_price import (
    GetStockPrice,
    GetStockPriceRequest,
    StockNotFound,
)


class TestGetStockPrice:
    """Test suite for GetStockPrice use case."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_provider = Mock(spec=StockPriceProvider)

    def test_handle_returns_stock_price_from_provider(self):
        """Test that handle() returns the stock price from the provider."""
        # Arrange
        ticker = "AAPL"
        expected_response = StockPriceResponse(
            ticker=ticker,
            price=Decimal("150.25"),
            currency="USD"
        )
        self.mock_provider.get_stock_price.return_value = expected_response

        use_case = GetStockPrice(provider=self.mock_provider)
        request = GetStockPriceRequest(ticker=ticker)

        # Act
        result = use_case.handle(request)

        # Assert
        assert result == expected_response
        self.mock_provider.get_stock_price.assert_called_once_with(ticker)

    def test_handle_raises_stock_not_found_when_provider_returns_none(self):
        """Test that handle() raises StockNotFound when provider returns None."""
        # Arrange
        ticker = "INVALID"
        self.mock_provider.get_stock_price.return_value = None

        use_case = GetStockPrice(provider=self.mock_provider)
        request = GetStockPriceRequest(ticker=ticker)

        # Act & Assert
        with pytest.raises(StockNotFound) as exc_info:
            use_case.handle(request)

        assert exc_info.value.ticker == ticker
        assert str(exc_info.value) == f"Stock not found: {ticker}"
        self.mock_provider.get_stock_price.assert_called_once_with(ticker)
