from ....application.providers import StockPriceProvider
from ....application.use_cases.get_stock_price import GetStockPrice
from ....application.use_cases.get_stocks_prices import GetStocksPrices
from ....application.use_cases.send_messages import SendMessages
from ....infrastructure.providers import YahooFinanceProvider
from .get_stock_price import GetStockPriceCommand
from .get_stocks_prices import GetStocksPricesCommand
from .registry import CommandRegistry
from .send_messages import HardcodedMessageSender, SendMessagesCommand


class CommandFactory:
    def __init__(self, stock_price_provider: StockPriceProvider) -> None:
        self._stock_price_provider = stock_price_provider

    def create_get_stock_price_command(self) -> GetStockPriceCommand:
        use_case = GetStockPrice(provider=self._stock_price_provider)
        return GetStockPriceCommand(get_stock_price_use_case=use_case)

    def create_get_stocks_prices_command(self) -> GetStocksPricesCommand:
        use_case = GetStocksPrices(provider=self._stock_price_provider)
        return GetStocksPricesCommand(get_stocks_prices_use_case=use_case)

    def create_send_messages_command(self) -> SendMessagesCommand:
        sender = HardcodedMessageSender()
        use_case = SendMessages(sender=sender)
        return SendMessagesCommand(send_messages_use_case=use_case)

    def create_command_registry(self) -> CommandRegistry:
        registry = CommandRegistry()
        registry.register(self.create_get_stock_price_command())
        registry.register(self.create_get_stocks_prices_command())
        registry.register(self.create_send_messages_command())
        return registry
