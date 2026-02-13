import argparse
import json
import logging
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from ...application.services import NotificationService
from ...application.use_cases.trigger_stocks_notifications import (
    TriggerStocksNotifications,
    TriggerStocksNotificationsRequest,
)
from ...infrastructure.factories import SettingsFactory
from ...infrastructure.implementations import TelegramMessageSender, YahooFinanceProvider
from pryces.infrastructure.logging import setup as setup_logging


@dataclass(frozen=True, slots=True)
class MonitorStocksConfig:
    iterations: int
    interval: int
    symbols: list[str]

    def __post_init__(self) -> None:
        if not isinstance(self.iterations, int) or self.iterations <= 0:
            raise ValueError("iterations must be a positive integer")
        if not isinstance(self.interval, int) or self.interval <= 0:
            raise ValueError("interval must be a positive integer")
        if not isinstance(self.symbols, list) or not self.symbols:
            raise ValueError("symbols must be a non-empty list")


def _get_config(path: Path) -> MonitorStocksConfig:
    data = json.loads(path.read_text())
    return MonitorStocksConfig(**data)


def _create_use_case() -> TriggerStocksNotifications:
    provider = YahooFinanceProvider()
    telegram_settings = SettingsFactory.create_telegram_settings()
    message_sender = TelegramMessageSender(settings=telegram_settings)
    notification_service = NotificationService(message_sender)
    return TriggerStocksNotifications(provider=provider, notification_service=notification_service)


def _monitor(
    use_case: TriggerStocksNotifications,
    config: MonitorStocksConfig,
    logger: logging.Logger,
) -> None:
    request = TriggerStocksNotificationsRequest(symbols=config.symbols)

    for i in range(config.iterations):
        try:
            use_case.handle(request)
        except Exception as e:
            logger.warning(f"Exception caught: {e}")

        if i < config.iterations - 1:
            time.sleep(config.interval)

    logger.info(
        f"Monitoring complete. {len(config.symbols)} stocks checked "
        f"over {config.iterations} repetitions."
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Monitor stocks for relevant price notifications",
    )
    parser.add_argument("config", type=Path, help="Path to the JSON configuration file")
    args = parser.parse_args()

    load_dotenv()
    setup_logging(verbose=True)
    logger = logging.getLogger(__name__)

    try:
        config = _get_config(args.config)
    except FileNotFoundError:
        print(f"Error: config file not found: {args.config}")
        return 1
    except (json.JSONDecodeError, TypeError, ValueError) as e:
        print(f"Error: invalid config file: {e}")
        return 1

    logger.info(f"Config: {args.config}")
    logger.info(
        f"Iterations: {config.iterations}, Interval: {config.interval}s, Stocks: {config.symbols}"
    )

    use_case = _create_use_case()
    _monitor(use_case, config, logger)

    return 0


if __name__ == "__main__":
    sys.exit(main())
