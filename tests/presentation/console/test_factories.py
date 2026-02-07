from decimal import Decimal
from unittest.mock import Mock

from pryces.application.messages import MessageSender
from pryces.application.providers import StockPriceProvider, StockPrice
from pryces.presentation.console.factories import CommandFactory
from pryces.presentation.console.commands.get_stock_price import GetStockPriceCommand
from pryces.presentation.console.commands.get_stocks_prices import GetStocksPricesCommand
from pryces.presentation.console.commands.registry import CommandRegistry
from pryces.presentation.console.commands.send_messages import SendMessagesCommand
from tests.fixtures.factories import create_stock_price


class TestCommandFactory:

    def test_init_accepts_custom_provider_and_message_sender(self):
        custom_provider = Mock(spec=StockPriceProvider)
        custom_sender = Mock(spec=MessageSender)

        factory = CommandFactory(stock_price_provider=custom_provider, message_sender=custom_sender)

        assert factory._stock_price_provider is custom_provider
        assert factory._message_sender is custom_sender

    def test_create_get_stock_price_command_returns_command_instance(self):
        mock_provider = Mock(spec=StockPriceProvider)
        factory = CommandFactory(
            stock_price_provider=mock_provider, message_sender=Mock(spec=MessageSender)
        )

        command = factory.create_get_stock_price_command()

        assert isinstance(command, GetStockPriceCommand)

    def test_create_get_stock_price_command_wires_dependencies_correctly(self):
        mock_provider = Mock(spec=StockPriceProvider)
        mock_provider.get_stock_price.return_value = create_stock_price(
            "TEST",
            Decimal("100.00"),
            name="Test Company",
            previousClosePrice=Decimal("99.00"),
            openPrice=Decimal("99.50"),
            dayHigh=Decimal("101.00"),
            dayLow=Decimal("98.00"),
            fiftyDayAverage=Decimal("100.00"),
            twoHundredDayAverage=Decimal("100.00"),
            fiftyTwoWeekHigh=Decimal("120.00"),
            fiftyTwoWeekLow=Decimal("80.00"),
        )
        factory = CommandFactory(
            stock_price_provider=mock_provider, message_sender=Mock(spec=MessageSender)
        )

        command = factory.create_get_stock_price_command()
        result = command.execute("TEST")

        assert "TEST" in result
        assert "100.00" in result
        mock_provider.get_stock_price.assert_called_once()

    def test_create_get_stock_price_command_with_default_provider(self):
        mock_provider = Mock(spec=StockPriceProvider)
        mock_provider.get_stock_price.return_value = create_stock_price(
            "AAPL", Decimal("150.25"), name="Apple Inc."
        )
        factory = CommandFactory(
            stock_price_provider=mock_provider, message_sender=Mock(spec=MessageSender)
        )

        command = factory.create_get_stock_price_command()
        result = command.execute("AAPL")

        assert '"success": true' in result
        assert "AAPL" in result
        assert "150.25" in result

    def test_create_command_registry_returns_registry_instance(self):
        mock_provider = Mock(spec=StockPriceProvider)
        factory = CommandFactory(
            stock_price_provider=mock_provider, message_sender=Mock(spec=MessageSender)
        )

        registry = factory.create_command_registry()

        assert isinstance(registry, CommandRegistry)

    def test_registry_contains_get_stock_price_command(self):
        mock_provider = Mock(spec=StockPriceProvider)
        factory = CommandFactory(
            stock_price_provider=mock_provider, message_sender=Mock(spec=MessageSender)
        )

        registry = factory.create_command_registry()
        all_commands = registry.get_all_commands()

        assert len(all_commands) > 0
        command = registry.get_command("get_stock_price")
        assert isinstance(command, GetStockPriceCommand)

    def test_registry_commands_are_functional(self):
        mock_provider = Mock(spec=StockPriceProvider)
        mock_provider.get_stock_price.return_value = create_stock_price(
            "AAPL", Decimal("150.25"), name="Apple Inc."
        )
        factory = CommandFactory(
            stock_price_provider=mock_provider, message_sender=Mock(spec=MessageSender)
        )

        registry = factory.create_command_registry()
        command = registry.get_command("get_stock_price")
        result = command.execute(symbol="AAPL")

        assert '"success": true' in result
        assert "AAPL" in result

    def test_create_get_stocks_prices_command_returns_command_instance(self):
        mock_provider = Mock(spec=StockPriceProvider)
        factory = CommandFactory(
            stock_price_provider=mock_provider, message_sender=Mock(spec=MessageSender)
        )

        command = factory.create_get_stocks_prices_command()

        assert isinstance(command, GetStocksPricesCommand)

    def test_create_get_stocks_prices_command_wires_dependencies_correctly(self):
        mock_provider = Mock(spec=StockPriceProvider)
        mock_provider.get_stocks_prices.return_value = [
            create_stock_price("AAPL", Decimal("150.25"), name="Apple Inc."),
            create_stock_price("GOOGL", Decimal("2847.50"), name="Alphabet Inc."),
        ]
        factory = CommandFactory(
            stock_price_provider=mock_provider, message_sender=Mock(spec=MessageSender)
        )

        command = factory.create_get_stocks_prices_command()
        result = command.execute("AAPL,GOOGL")

        assert "AAPL" in result
        assert "GOOGL" in result
        assert "150.25" in result
        assert "2847.50" in result
        mock_provider.get_stocks_prices.assert_called_once()

    def test_registry_contains_get_stocks_prices_command(self):
        mock_provider = Mock(spec=StockPriceProvider)
        factory = CommandFactory(
            stock_price_provider=mock_provider, message_sender=Mock(spec=MessageSender)
        )

        registry = factory.create_command_registry()
        command = registry.get_command("get_stocks_prices")

        assert isinstance(command, GetStocksPricesCommand)

    def test_registry_contains_send_messages_command(self):
        mock_provider = Mock(spec=StockPriceProvider)
        factory = CommandFactory(
            stock_price_provider=mock_provider, message_sender=Mock(spec=MessageSender)
        )

        registry = factory.create_command_registry()
        command = registry.get_command("send_messages")

        assert isinstance(command, SendMessagesCommand)

    def test_registry_get_stocks_prices_command_is_functional(self):
        mock_provider = Mock(spec=StockPriceProvider)
        mock_provider.get_stocks_prices.return_value = [
            create_stock_price("AAPL", Decimal("150.25"), name="Apple Inc."),
            create_stock_price("GOOGL", Decimal("2847.50"), name="Alphabet Inc."),
            create_stock_price("MSFT", Decimal("350.75"), name="Microsoft Corporation"),
        ]
        factory = CommandFactory(
            stock_price_provider=mock_provider, message_sender=Mock(spec=MessageSender)
        )

        registry = factory.create_command_registry()
        command = registry.get_command("get_stocks_prices")
        result = command.execute(symbols="AAPL,GOOGL,MSFT")

        assert '"success": true' in result
        assert "AAPL" in result
        assert "GOOGL" in result
        assert "MSFT" in result
