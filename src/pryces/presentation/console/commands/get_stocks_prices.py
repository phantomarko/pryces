import logging

from ....application.use_cases.get_stocks_prices import GetStocksPrices, GetStocksPricesRequest
from ..formatters import format_stock_list
from .base import Command, CommandMetadata, InputPrompt


def validate_symbols(value: str) -> bool:
    if not value or not value.strip():
        return False

    symbols = [s.strip() for s in value.split(",")]
    return all(symbol and len(symbol) <= 10 for symbol in symbols)


def parse_symbols_input(value: str) -> list[str]:
    symbols = [s.strip().upper() for s in value.split(",")]
    return [s for s in symbols if s]


class GetStocksPricesCommand(Command):
    def __init__(self, get_stocks_prices_use_case: GetStocksPrices) -> None:
        self._get_stocks_prices = get_stocks_prices_use_case
        self._logger = logging.getLogger(__name__)

    def get_metadata(self) -> CommandMetadata:
        return CommandMetadata(
            id="get_stocks_prices",
            name="Get Multiple Stock Prices",
            description="Retrieve current prices for multiple stock symbols",
        )

    def get_input_prompts(self) -> list[InputPrompt]:
        return [
            InputPrompt(
                key="symbols",
                prompt="Enter stock symbols separated by commas (e.g., AAPL,GOOGL,MSFT): ",
                validator=validate_symbols,
            )
        ]

    def execute(self, symbols: str = None, **kwargs) -> str:
        self._logger.info(f"Fetching stock prices for symbols: {symbols}")

        try:
            symbol_list = parse_symbols_input(symbols)
            request = GetStocksPricesRequest(symbols=symbol_list)
            responses = self._get_stocks_prices.handle(request)

            self._logger.info(
                f"Successfully retrieved prices for {len(responses)}/{len(symbol_list)} symbols"
            )

            return format_stock_list(responses, requested_count=len(symbol_list))

        except Exception as e:
            self._logger.exception(f"Unexpected error while fetching stock prices for {symbols}")

            return f"Error: An unexpected error occurred: {e}"
