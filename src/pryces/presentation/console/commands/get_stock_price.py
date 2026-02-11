from ....application.exceptions import StockNotFound
from ....application.use_cases.get_stock_price import GetStockPrice, GetStockPriceRequest
from ..output_utils import format_stock
from .base import Command, CommandMetadata, InputPrompt
from ..input_utils import validate_symbol


class GetStockPriceCommand(Command):
    def __init__(self, get_stock_price_use_case: GetStockPrice) -> None:
        self._get_stock_price = get_stock_price_use_case

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
        try:
            request = GetStockPriceRequest(symbol=symbol)
            response = self._get_stock_price.handle(request)

            return format_stock(response)

        except StockNotFound as e:
            return f"Error: {e}"

        except Exception as e:
            return f"Error: An unexpected error occurred: {e}"
