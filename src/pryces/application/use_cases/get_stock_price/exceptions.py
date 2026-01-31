"""Exceptions for get stock price use case."""


class StockNotFound(Exception):
    """Raised when a stock ticker cannot be found.

    Attributes:
        ticker: The stock ticker that was not found
    """

    def __init__(self, ticker: str) -> None:
        """Initialize the exception.

        Args:
            ticker: The stock ticker that was not found
        """
        self.ticker = ticker
        super().__init__(f"Stock not found: {ticker}")
