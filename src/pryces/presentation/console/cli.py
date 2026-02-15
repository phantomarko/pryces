import logging
import os
import sys

from dotenv import load_dotenv

from ...infrastructure.factories import SettingsFactory
from ...infrastructure.implementations import TelegramMessageSender, YahooFinanceProvider
from ...infrastructure.logging import setup as setup_logging
from .factories import CommandFactory
from .menu import InteractiveMenu


def _create_menu() -> InteractiveMenu:
    max_workers = int(os.environ["MAX_FETCH_WORKERS"])
    provider = YahooFinanceProvider(max_workers=max_workers)

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

    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        menu = _create_menu()
        menu.run()
        return 0

    except Exception as e:
        logger.error(f"CLI error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
