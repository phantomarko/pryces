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
from ...infrastructure.implementations import (
    InMemoryNotificationRepository,
    InMemoryStockRepository,
    TelegramMessageSender,
    YahooFinanceProvider,
)
from pryces.infrastructure.logging import setup_monitor_logging


@dataclass(frozen=True, slots=True)
class MonitorStocksConfig:
    duration: int
    interval: int
    symbols: list[str]

    def __post_init__(self) -> None:
        if not isinstance(self.duration, int) or self.duration <= 0:
            raise ValueError("duration must be a positive integer")
        if not isinstance(self.interval, int) or self.interval <= 0:
            raise ValueError("interval must be a positive integer")
        if not isinstance(self.symbols, list) or not self.symbols:
            raise ValueError("symbols must be a non-empty list")


class MonitorStocksScript:
    def __init__(
        self,
        use_case: TriggerStocksNotifications,
        config: MonitorStocksConfig,
    ) -> None:
        self._use_case = use_case
        self._config = config
        self._logger = logging.getLogger(__name__)

    def run(self) -> None:
        self._logger.info(f"Config: {self._config}")
        self._logger.info(
            f"Duration: {self._config.duration}m, Interval: {self._config.interval}s, "
            f"Stocks: {self._config.symbols}"
        )
        request = TriggerStocksNotificationsRequest(symbols=self._config.symbols)
        duration_seconds = self._config.duration * 60
        start = time.monotonic()

        while True:
            try:
                self._use_case.handle(request)
            except Exception as e:
                self._logger.warning(f"Exception caught: {e}")

            if time.monotonic() - start >= duration_seconds:
                break

            time.sleep(self._config.interval)

        self._logger.info(
            f"Monitoring complete. {len(self._config.symbols)} stocks checked "
            f"over {self._config.duration} minutes."
        )


def _get_config(path: Path) -> MonitorStocksConfig:
    data = json.loads(path.read_text())
    return MonitorStocksConfig(**data)


def _create_script(config: MonitorStocksConfig) -> MonitorStocksScript:
    yahoo_finance_settings = SettingsFactory.create_yahoo_finance_settings()
    provider = YahooFinanceProvider(settings=yahoo_finance_settings)
    telegram_settings = SettingsFactory.create_telegram_settings()
    message_sender = TelegramMessageSender(settings=telegram_settings)
    notification_repository = InMemoryNotificationRepository()
    notification_service = NotificationService(message_sender, notification_repository)
    stock_repository = InMemoryStockRepository()
    use_case = TriggerStocksNotifications(
        provider=provider,
        notification_service=notification_service,
        stock_repository=stock_repository,
    )
    return MonitorStocksScript(use_case, config)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Monitor stocks for relevant price notifications",
    )
    parser.add_argument("config", type=Path, help="Path to the JSON configuration file")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    load_dotenv()
    setup_monitor_logging(debug=args.debug)

    try:
        config = _get_config(args.config)
    except FileNotFoundError:
        print(f"Error: config file not found: {args.config}")
        return 1
    except (json.JSONDecodeError, TypeError, ValueError) as e:
        print(f"Error: invalid config file: {e}")
        return 1

    try:
        script = _create_script(config)
        script.run()
    except Exception as e:
        message = f"Monitor error: {e}"
        print(message)
        logging.getLogger(__name__).error(message)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
