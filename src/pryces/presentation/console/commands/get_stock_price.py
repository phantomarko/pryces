"""Console command for getting stock prices."""

import json
import logging
from dataclasses import asdict
from decimal import Decimal
from typing import Any

from ....application.use_cases.get_stock_price.dtos import GetStockPriceRequest
from ....application.use_cases.get_stock_price.exceptions import StockNotFound
from ....application.use_cases.get_stock_price.get_stock_price import GetStockPrice


class DecimalEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles Decimal types.

    Converts Decimal to string to preserve precision in JSON output.
    """

    def default(self, obj: Any) -> Any:
        """Encode Decimal as string, otherwise use default encoder.

        Args:
            obj: Object to encode

        Returns:
            String representation for Decimal, default encoding otherwise
        """
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)


class GetStockPriceCommand:
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

    def execute(self, ticker: str) -> str:
        """Execute the command to get stock price for a ticker.

        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL', 'GOOGL')

        Returns:
            JSON string containing either:
                - Success: {"success": true, "data": {"ticker": "...", "price": "...", "currency": "..."}}
                - Error: {"success": false, "error": {"code": "...", "message": "..."}}
        """
        self._logger.info(f"Fetching stock price for ticker: {ticker}")

        try:
            request = GetStockPriceRequest(ticker=ticker)
            response = self._get_stock_price.handle(request)

            self._logger.info(f"Successfully retrieved price for {ticker}")

            result = {
                "success": True,
                "data": asdict(response)
            }

            return json.dumps(result, cls=DecimalEncoder, indent=2)

        except StockNotFound as e:
            self._logger.error(f"Stock not found: {ticker}")

            result = {
                "success": False,
                "error": {
                    "code": "STOCK_NOT_FOUND",
                    "message": str(e)
                }
            }

            return json.dumps(result, indent=2)

        except Exception as e:
            self._logger.exception(f"Unexpected error while fetching stock price for {ticker}")

            result = {
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": f"An unexpected error occurred: {str(e)}"
                }
            }

            return json.dumps(result, indent=2)
