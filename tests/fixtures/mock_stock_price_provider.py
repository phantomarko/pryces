"""Mock stock price provider for testing."""

from decimal import Decimal

from pryces.application.providers import StockPriceProvider, StockPriceResponse


class MockStockPriceProvider(StockPriceProvider):
    """Mock stock price provider for demonstration purposes.

    This is a temporary implementation for testing and demonstration.
    Replace with a real provider implementation (e.g., YahooFinanceProvider,
    AlphaVantageProvider) in production.
    """

    def get_stock_price(self, symbol: str) -> StockPriceResponse | None:
        """Return mock stock price data.

        Args:
            symbol: Stock ticker symbol

        Returns:
            StockPriceResponse with mock data if symbol exists, None otherwise
        """
        # Mock data with all price fields
        mock_data = {
            "AAPL": {
                "name": "Apple Inc.",
                "currentPrice": Decimal("150.25"),
                "previousClose": Decimal("148.50"),
                "open": Decimal("149.00"),
                "dayHigh": Decimal("151.00"),
                "dayLow": Decimal("148.00"),
                "fiftyDayAvg": Decimal("145.50"),
                "twoHundredDayAvg": Decimal("140.00"),
                "fiftyTwoWeekHigh": Decimal("180.00"),
                "fiftyTwoWeekLow": Decimal("120.00"),
            },
            "GOOGL": {
                "name": "Alphabet Inc.",
                "currentPrice": Decimal("2847.50"),
                "previousClose": Decimal("2830.00"),
                "open": Decimal("2835.00"),
                "dayHigh": Decimal("2850.00"),
                "dayLow": Decimal("2825.00"),
                "fiftyDayAvg": Decimal("2800.00"),
                "twoHundredDayAvg": Decimal("2750.00"),
                "fiftyTwoWeekHigh": Decimal("3000.00"),
                "fiftyTwoWeekLow": Decimal("2500.00"),
            },
            "TSLA": {
                "name": "Tesla, Inc.",
                "currentPrice": Decimal("200.00"),
                "previousClose": Decimal("198.50"),
                "open": Decimal("199.00"),
                "dayHigh": Decimal("202.00"),
                "dayLow": Decimal("197.00"),
                "fiftyDayAvg": Decimal("195.00"),
                "twoHundredDayAvg": Decimal("190.00"),
                "fiftyTwoWeekHigh": Decimal("250.00"),
                "fiftyTwoWeekLow": Decimal("150.00"),
            },
            "MSFT": {
                "name": "Microsoft Corporation",
                "currentPrice": Decimal("350.75"),
                "previousClose": Decimal("348.00"),
                "open": Decimal("349.00"),
                "dayHigh": Decimal("352.00"),
                "dayLow": Decimal("347.00"),
                "fiftyDayAvg": Decimal("345.00"),
                "twoHundredDayAvg": Decimal("340.00"),
                "fiftyTwoWeekHigh": Decimal("380.00"),
                "fiftyTwoWeekLow": Decimal("300.00"),
            },
        }

        symbol_upper = symbol.upper()
        if symbol_upper in mock_data:
            data = mock_data[symbol_upper]
            return StockPriceResponse(
                symbol=symbol_upper,
                name=data["name"],
                currentPrice=data["currentPrice"],
                currency="USD",
                previousClosePrice=data["previousClose"],
                openPrice=data["open"],
                dayHigh=data["dayHigh"],
                dayLow=data["dayLow"],
                fiftyDayAverage=data["fiftyDayAvg"],
                twoHundredDayAverage=data["twoHundredDayAvg"],
                fiftyTwoWeekHigh=data["fiftyTwoWeekHigh"],
                fiftyTwoWeekLow=data["fiftyTwoWeekLow"]
            )
        return None
