import logging

from ....application.exceptions import StockNotFound
from ....application.use_cases.get_stock_price import GetStockPrice, GetStockPriceRequest
from ..utils import format_stock, validate_symbol
from .base import Command, CommandMetadata, InputPrompt


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
        self._logger.info("Get Stock Price command started")
        self._logger.info(f"Symbol: {symbol}")
        try:
            request = GetStockPriceRequest(symbol=symbol)
            response = self._get_stock_price.handle(request)

            self._logger.info("Get Stock Price command finished")
            return format_stock(response)

        except StockNotFound as e:
            self._logger.error(f"Get Stock Price command finished with errors: {e}")
            return f"Error: {e}"

        except Exception as e:
            self._logger.error(f"Get Stock Price command finished with errors: {e}")
            return f"Error: An unexpected error occurred: {e}"
