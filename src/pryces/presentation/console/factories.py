import os

from ...application.interfaces import StockProvider, MessageSender
from ...application.use_cases.get_stock_price import GetStockPrice
from ...application.use_cases.get_stocks_prices import GetStocksPrices
from ...application.use_cases.send_messages import SendMessages
from ...infrastructure.implementations import TelegramSettings
from .commands.get_stock_price import GetStockPriceCommand
from .commands.get_stocks_prices import GetStocksPricesCommand
from .commands.registry import CommandRegistry
from .commands.send_messages import SendMessagesCommand


class CommandFactory:
    def __init__(self, stock_provider: StockProvider, message_sender: MessageSender) -> None:
        self._stock_provider = stock_provider
        self._message_sender = message_sender

    def create_get_stock_price_command(self) -> GetStockPriceCommand:
        use_case = GetStockPrice(provider=self._stock_provider)
        return GetStockPriceCommand(get_stock_price_use_case=use_case)

    def create_get_stocks_prices_command(self) -> GetStocksPricesCommand:
        use_case = GetStocksPrices(provider=self._stock_provider)
        return GetStocksPricesCommand(get_stocks_prices_use_case=use_case)

    def create_send_messages_command(self) -> SendMessagesCommand:
        use_case = SendMessages(sender=self._message_sender)
        return SendMessagesCommand(send_messages_use_case=use_case)

    def create_command_registry(self) -> CommandRegistry:
        registry = CommandRegistry()
        registry.register(self.create_get_stock_price_command())
        registry.register(self.create_get_stocks_prices_command())
        registry.register(self.create_send_messages_command())
        return registry


class SettingsFactory:
    @staticmethod
    def create_telegram_settings() -> TelegramSettings:
        return TelegramSettings(
            bot_token=os.environ["TELEGRAM_BOT_TOKEN"],
            group_id=os.environ["TELEGRAM_GROUP_ID"],
        )
