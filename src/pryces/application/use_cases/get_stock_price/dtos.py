"""Data Transfer Objects for get stock price use case."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GetStockPriceRequest:
    """Request DTO for getting stock price.

    Attributes:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'GOOGL')
    """
    ticker: str
