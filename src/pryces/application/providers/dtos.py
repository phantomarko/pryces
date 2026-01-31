"""Data Transfer Objects for providers."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class StockPriceResponse:
    """Response DTO for stock price queries.

    Attributes:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'GOOGL')
        price: Current stock price as a Decimal for precision
        currency: Currency code (e.g., 'USD', 'EUR')
    """
    ticker: str
    price: Decimal
    currency: str
