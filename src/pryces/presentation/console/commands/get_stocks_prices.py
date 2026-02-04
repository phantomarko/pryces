"""Console command for getting multiple stock prices."""

import logging
from dataclasses import asdict

from ....application.use_cases.get_stocks_prices import GetStocksPrices, GetStocksPricesRequest
from ..json_utils import to_json
from .base import Command, CommandMetadata, InputPrompt


def validate_symbols(value: str) -> bool:
    if not value or not value.strip():
        return False

    symbols = [s.strip() for s in value.split(',')]
    return all(symbol and len(symbol) <= 10 for symbol in symbols)


def parse_symbols_input(value: str) -> list[str]:
    symbols = [s.strip().upper() for s in value.split(',')]
    return [s for s in symbols if s]


class GetStocksPricesCommand(Command):
    """Console command for retrieving multiple stock prices.

    This command provides a CLI interface to the GetStocksPrices use case,
    outputting results as JSON for easy parsing and integration.
    """

    def __init__(self, get_stocks_prices_use_case: GetStocksPrices) -> None:
        self._get_stocks_prices = get_stocks_prices_use_case
        self._logger = logging.getLogger(__name__)

    def get_metadata(self) -> CommandMetadata:
        return CommandMetadata(
            id="get_stocks_prices",
            name="Get Multiple Stock Prices",
            description="Retrieve current prices for multiple stock symbols"
        )

    def get_input_prompts(self) -> list[InputPrompt]:
        return [
            InputPrompt(
                key="symbols",
                prompt="Enter stock symbols separated by commas (e.g., AAPL,GOOGL,MSFT): ",
                validator=validate_symbols
            )
        ]

    def execute(self, symbols: str = None, **kwargs) -> str:
        """Execute the command to get stock prices for multiple symbols.

        Returns:
            JSON string with success/error structure
        """
        self._logger.info(f"Fetching stock prices for symbols: {symbols}")

        try:
            symbol_list = parse_symbols_input(symbols)
            request = GetStocksPricesRequest(symbols=symbol_list)
            responses = self._get_stocks_prices.handle(request)

            self._logger.info(f"Successfully retrieved prices for {len(responses)}/{len(symbol_list)} symbols")

            # Build summary statistics
            requested_count = len(symbol_list)
            successful_count = len(responses)
            failed_count = requested_count - successful_count

            result = {
                "success": True,
                "data": [asdict(response) for response in responses],
                "summary": {
                    "requested": requested_count,
                    "successful": successful_count,
                    "failed": failed_count
                }
            }

            return to_json(result)

        except Exception as e:
            self._logger.exception(f"Unexpected error while fetching stock prices for {symbols}")

            result = {
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": f"An unexpected error occurred: {str(e)}"
                }
            }

            return to_json(result)
