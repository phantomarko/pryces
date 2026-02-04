"""Application layer exceptions.

This module contains domain-specific exceptions used across the application layer.
"""


class StockNotFound(Exception):
    """Raised when a stock symbol cannot be found.

    Attributes:
        symbol: The stock symbol that was not found
    """

    def __init__(self, symbol: str) -> None:
        self.symbol = symbol
        super().__init__(f"Stock not found: {symbol}")


class StockInformationIncomplete(Exception):
    """Raised when required stock price information is not available.

    This exception is thrown when the provider can find the stock but
    cannot retrieve the required current price field from the data source.

    Attributes:
        symbol: The stock symbol that has incomplete information
    """

    def __init__(self, symbol: str) -> None:
        self.symbol = symbol
        super().__init__(f"Stock information incomplete: unable to retrieve current price for {symbol}")
