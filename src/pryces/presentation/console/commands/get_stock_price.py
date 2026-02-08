import logging

from ....application.exceptions import StockNotFound
from ....application.use_cases.get_stock_price import GetStockPrice, GetStockPriceRequest
from ..formatters import format_stock
from .base import Command, CommandMetadata, InputPrompt


def validate_symbol(value: str) -> bool:
    return bool(value and value.strip() and len(value.strip()) <= 10)


class GetStockPriceCommand(Command):
    def __init__(self, get_stock_price_use_case: GetStockPrice) -> None:
        self._get_stock_price = get_stock_price_use_case
        self._logger = logging.getLogger(__name__)

    def get_metadata(self) -> CommandMetadata:
        return CommandMetadata(
            id="get_stock_price",
            name="Get Stock Price",
            description="Retrieve current price and details for a single stock symbol",
        )

    def get_input_prompts(self) -> list[InputPrompt]:
        return [
            InputPrompt(
                key="symbol",
                prompt="Enter stock symbol (e.g., AAPL, GOOGL): ",
                validator=validate_symbol,
            )
        ]

    def execute(self, symbol: str = None, **kwargs) -> str:
        self._logger.info(f"Fetching stock price for symbol: {symbol}")

        try:
            request = GetStockPriceRequest(symbol=symbol)
            response = self._get_stock_price.handle(request)

            self._logger.info(f"Successfully retrieved price for {symbol}")

            return format_stock(response)

        except StockNotFound as e:
            self._logger.error(f"Stock not found: {symbol}")

            return f"Error: {e}"

        except Exception as e:
            self._logger.exception(f"Unexpected error while fetching stock price for {symbol}")

            return f"Error: An unexpected error occurred: {e}"
