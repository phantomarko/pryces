from unittest.mock import Mock

from pryces.application.interfaces import StockProvider, MessageSender
from pryces.presentation.console.factories import CommandFactory
from pryces.presentation.console.commands.get_stock_price import GetStockPriceCommand
from pryces.presentation.console.commands.get_stocks_prices import GetStocksPricesCommand
from pryces.presentation.console.commands.monitor_stocks import MonitorStocksCommand
from pryces.presentation.console.commands.registry import CommandRegistry
from pryces.presentation.console.commands.check_readiness import CheckReadinessCommand


class TestCommandFactory:

    def test_init_accepts_custom_provider_and_message_sender(self):
        custom_provider = Mock(spec=StockProvider)
        custom_sender = Mock(spec=MessageSender)

        factory = CommandFactory(stock_provider=custom_provider, message_sender=custom_sender)

        assert factory._stock_provider is custom_provider
        assert factory._message_sender is custom_sender

    def test__create_get_stock_price_command_returns_command_instance(self):
        mock_provider = Mock(spec=StockProvider)
        factory = CommandFactory(
            stock_provider=mock_provider, message_sender=Mock(spec=MessageSender)
        )

        command = factory._create_get_stock_price_command()

        assert isinstance(command, GetStockPriceCommand)

    def test_create_command_registry_returns_registry_instance(self):
        mock_provider = Mock(spec=StockProvider)
        factory = CommandFactory(
            stock_provider=mock_provider, message_sender=Mock(spec=MessageSender)
        )

        registry = factory.create_command_registry()

        assert isinstance(registry, CommandRegistry)

    def test_registry_contains_get_stock_price_command(self):
        mock_provider = Mock(spec=StockProvider)
        factory = CommandFactory(
            stock_provider=mock_provider, message_sender=Mock(spec=MessageSender)
        )

        registry = factory.create_command_registry()
        all_commands = registry.get_all_commands()

        assert len(all_commands) > 0
        command = registry.get_command("get_stock_price")
        assert isinstance(command, GetStockPriceCommand)

    def test__create_get_stocks_prices_command_returns_command_instance(self):
        mock_provider = Mock(spec=StockProvider)
        factory = CommandFactory(
            stock_provider=mock_provider, message_sender=Mock(spec=MessageSender)
        )

        command = factory._create_get_stocks_prices_command()

        assert isinstance(command, GetStocksPricesCommand)

    def test_registry_contains_get_stocks_prices_command(self):
        mock_provider = Mock(spec=StockProvider)
        factory = CommandFactory(
            stock_provider=mock_provider, message_sender=Mock(spec=MessageSender)
        )

        registry = factory.create_command_registry()
        command = registry.get_command("get_stocks_prices")

        assert isinstance(command, GetStocksPricesCommand)

    def test_registry_contains_check_readiness_command(self):
        mock_provider = Mock(spec=StockProvider)
        factory = CommandFactory(
            stock_provider=mock_provider, message_sender=Mock(spec=MessageSender)
        )

        registry = factory.create_command_registry()
        command = registry.get_command("check_readiness")

        assert isinstance(command, CheckReadinessCommand)

    def test_registry_contains_monitor_stocks_command(self):
        mock_provider = Mock(spec=StockProvider)
        factory = CommandFactory(
            stock_provider=mock_provider, message_sender=Mock(spec=MessageSender)
        )

        registry = factory.create_command_registry()
        command = registry.get_command("monitor_stocks")

        assert isinstance(command, MonitorStocksCommand)

    def test_monitor_stocks_is_first_command_in_registry(self):
        mock_provider = Mock(spec=StockProvider)
        factory = CommandFactory(
            stock_provider=mock_provider, message_sender=Mock(spec=MessageSender)
        )

        registry = factory.create_command_registry()
        all_commands = registry.get_all_commands()

        assert all_commands[0].get_metadata().id == "monitor_stocks"
