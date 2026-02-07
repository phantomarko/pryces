import argparse
import logging
import sys

from dotenv import load_dotenv

from ...infrastructure.implementations import TelegramMessageSender, YahooFinanceProvider
from .factories import CommandFactory, SettingsFactory
from .menu import InteractiveMenu


def configure_logging(verbose: bool = False) -> None:
    log_level = logging.INFO if verbose else logging.WARNING
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )


def create_menu() -> InteractiveMenu:
    provider = YahooFinanceProvider()

    telegram_settings = SettingsFactory.create_telegram_settings()
    message_sender = TelegramMessageSender(settings=telegram_settings)

    factory = CommandFactory(
        stock_provider=provider,
        message_sender=message_sender,
    )

    registry = factory.create_command_registry()
    return InteractiveMenu(registry)


def main() -> int:
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Stock price information system - Interactive Menu",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging to stderr"
    )

    args = parser.parse_args()

    configure_logging(args.verbose)

    try:
        menu = create_menu()
        menu.run()
        return 0

    except Exception as e:
        logging.error(f"CLI error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
