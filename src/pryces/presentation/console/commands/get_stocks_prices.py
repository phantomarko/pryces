from ....application.use_cases.get_stocks_prices import GetStocksPrices, GetStocksPricesRequest
from ..utils import format_stock_list, parse_symbols_input, validate_symbols
from .base import Command, CommandMetadata, InputPrompt


class GetStocksPricesCommand(Command):
    def __init__(self, get_stocks_prices_use_case: GetStocksPrices) -> None:
        self._get_stocks_prices = get_stocks_prices_use_case

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
        try:
            symbol_list = parse_symbols_input(symbols)
            request = GetStocksPricesRequest(symbols=symbol_list)
            responses = self._get_stocks_prices.handle(request)

            return format_stock_list(responses, requested_count=len(symbol_list))

        except Exception as e:
            return f"Error: An unexpected error occurred: {e}"
