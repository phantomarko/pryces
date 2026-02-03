"""Console command for getting stock prices."""

import logging
from dataclasses import asdict

from ....application.exceptions import StockNotFound
from ....application.use_cases.get_stock_price import GetStockPrice, GetStockPriceRequest
from ..json_utils import to_json
from .base import Command, CommandMetadata, InputPrompt


def validate_symbol(value: str) -> bool:
    """Validate stock symbol input."""
    return bool(value and value.strip() and len(value.strip()) <= 10)


class GetStockPriceCommand(Command):
    """Console command for retrieving stock price information.

    This command provides a CLI interface to the GetStockPrice use case,
    outputting results as JSON for easy parsing and integration.
    """

    def __init__(self, get_stock_price_use_case: GetStockPrice) -> None:
        """Initialize the command with the use case.

        Args:
            get_stock_price_use_case: GetStockPrice use case instance
        """
        self._get_stock_price = get_stock_price_use_case
        self._logger = logging.getLogger(__name__)

    def get_metadata(self) -> CommandMetadata:
        """Return metadata for menu display."""
        return CommandMetadata(
            id="get_stock_price",
            name="Get Stock Price",
            description="Retrieve current price and details for a single stock symbol"
        )

    def get_input_prompts(self) -> list[InputPrompt]:
        """Return input prompts for collecting symbol."""
        return [
            InputPrompt(
                key="symbol",
                prompt="Enter stock symbol (e.g., AAPL, GOOGL): ",
                validator=validate_symbol
            )
        ]

    def execute(self, symbol: str = None, **kwargs) -> str:
        """Execute the command to get stock price for a symbol.

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL', 'GOOGL')

        Returns:
            JSON string containing either:
                - Success: {
                    "success": true,
                    "data": {
                        "symbol": "..." (required),
                        "currentPrice": "..." (required),
                        "name": "..." (optional),
                        "currency": "..." (optional),
                        "previousClosePrice": "..." (optional),
                        "openPrice": "..." (optional),
                        "dayHigh": "..." (optional),
                        "dayLow": "..." (optional),
                        "fiftyDayAverage": "..." (optional),
                        "twoHundredDayAverage": "..." (optional),
                        "fiftyTwoWeekHigh": "..." (optional),
                        "fiftyTwoWeekLow": "..." (optional)
                    }
                }
                - Error: {"success": false, "error": {"code": "...", "message": "..."}}
        """
        self._logger.info(f"Fetching stock price for symbol: {symbol}")

        try:
            request = GetStockPriceRequest(symbol=symbol)
            response = self._get_stock_price.handle(request)

            self._logger.info(f"Successfully retrieved price for {symbol}")

            result = {
                "success": True,
                "data": asdict(response)
            }

            return to_json(result)

        except StockNotFound as e:
            self._logger.error(f"Stock not found: {symbol}")

            result = {
                "success": False,
                "error": {
                    "code": "STOCK_NOT_FOUND",
                    "message": str(e)
                }
            }

            return to_json(result)

        except Exception as e:
            self._logger.exception(f"Unexpected error while fetching stock price for {symbol}")

            result = {
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": f"An unexpected error occurred: {str(e)}"
                }
            }

            return to_json(result)
