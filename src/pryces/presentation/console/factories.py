from ...application.interfaces import StockProvider, MessageSender
from ...application.use_cases.get_stock_price import GetStockPrice
from ...application.use_cases.get_stocks_prices import GetStocksPrices
from ...application.use_cases.send_messages import SendMessages
from .commands.get_stock_price import GetStockPriceCommand
from .commands.get_stocks_prices import GetStocksPricesCommand
from .commands.monitor_stocks import MonitorStocksCommand
from .commands.registry import CommandRegistry
from .commands.check_readiness import CheckReadinessCommand
from .commands.list_monitors import ListMonitorsCommand
from .commands.stop_monitor import StopMonitorCommand


class CommandFactory:
    def __init__(self, stock_provider: StockProvider, message_sender: MessageSender) -> None:
        self._stock_provider = stock_provider
        self._message_sender = message_sender

    def _create_monitor_stocks_command(self) -> MonitorStocksCommand:
        return MonitorStocksCommand()

    def _create_get_stock_price_command(self) -> GetStockPriceCommand:
        use_case = GetStockPrice(provider=self._stock_provider)
        return GetStockPriceCommand(get_stock_price_use_case=use_case)

    def _create_get_stocks_prices_command(self) -> GetStocksPricesCommand:
        use_case = GetStocksPrices(provider=self._stock_provider)
        return GetStocksPricesCommand(get_stocks_prices_use_case=use_case)

    def _create_check_readiness_command(self) -> CheckReadinessCommand:
        use_case = SendMessages(sender=self._message_sender)
        return CheckReadinessCommand(send_messages_use_case=use_case)

    def _create_list_monitors_command(self) -> ListMonitorsCommand:
        return ListMonitorsCommand()

    def _create_stop_monitor_command(self) -> StopMonitorCommand:
        return StopMonitorCommand()

    def create_command_registry(self) -> CommandRegistry:
        registry = CommandRegistry()
        registry.register(self._create_monitor_stocks_command())
        registry.register(self._create_list_monitors_command())
        registry.register(self._create_stop_monitor_command())
        registry.register(self._create_get_stock_price_command())
        registry.register(self._create_get_stocks_prices_command())
        registry.register(self._create_check_readiness_command())
        return registry
