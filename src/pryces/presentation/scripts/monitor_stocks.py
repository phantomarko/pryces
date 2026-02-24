import argparse
import logging
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

from ...application.services import NotificationService
from ...application.use_cases.trigger_stocks_notifications import (
    TriggerStocksNotifications,
    TriggerStocksNotificationsRequest,
)
from ...infrastructure.factories import SettingsFactory
from ...infrastructure.implementations import (
    InMemoryMarketTransitionRepository,
    InMemoryNotificationRepository,
    InMemoryStockRepository,
    TelegramMessageSender,
    YahooFinanceProvider,
)
from pryces.infrastructure.logging import setup_monitor_logging
from .config import ConfigManager
from .exceptions import ConfigLoadingFailed


class MonitorStocksScript:
    def __init__(
        self,
        use_case: TriggerStocksNotifications,
        config_manager: ConfigManager,
    ) -> None:
        self._use_case = use_case
        self._config_manager = config_manager
        self._logger = logging.getLogger(__name__)
        self._config = self._config_manager.load_monitor_stocks_config()

    def _refresh_config(self) -> None:
        try:
            new_config = self._config_manager.load_monitor_stocks_config()
            if new_config != self._config:
                self._config = new_config
                self._logger.info("Config refreshed.")
                self._log_config()
        except Exception:
            pass

    def _log_config(self) -> None:
        duration_label = (
            f"{self._config.duration} minute{'s' if self._config.duration != 1 else ''}"
        )
        self._logger.info(f"Monitoring every {self._config.interval}s for {duration_label}.")
        stocks_info = [
            f"{s.symbol} @ {', '.join(str(p) for p in s.prices)}" for s in self._config.symbols
        ]
        self._logger.info(f"Stocks: {' | '.join(stocks_info)}")

    def run(self) -> None:
        self._logger.info("Monitoring started.")
        self._log_config()
        duration_seconds = self._config.duration * 60
        start = time.monotonic()

        while True:
            self._refresh_config()
            request = TriggerStocksNotificationsRequest(
                symbols=[s.symbol for s in self._config.symbols]
            )
            try:
                self._use_case.handle(request)
            except Exception as e:
                self._logger.warning(f"Exception caught: {e}")

            if time.monotonic() - start >= duration_seconds:
                break

            time.sleep(self._config.interval)

        self._logger.info("Monitoring finished.")


def _create_script(path: Path) -> MonitorStocksScript:
    yahoo_finance_settings = SettingsFactory.create_yahoo_finance_settings()
    provider = YahooFinanceProvider(settings=yahoo_finance_settings)
    telegram_settings = SettingsFactory.create_telegram_settings()
    message_sender = TelegramMessageSender(settings=telegram_settings)
    notification_repository = InMemoryNotificationRepository()
    transition_repository = InMemoryMarketTransitionRepository()
    notification_service = NotificationService(
        message_sender, notification_repository, transition_repository
    )
    stock_repository = InMemoryStockRepository()
    use_case = TriggerStocksNotifications(
        provider=provider,
        notification_service=notification_service,
        stock_repository=stock_repository,
    )
    return MonitorStocksScript(use_case, ConfigManager(path))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Monitor stocks for relevant price notifications",
    )
    parser.add_argument("config", type=Path, help="Path to the JSON configuration file")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging to stderr")
    args = parser.parse_args()

    load_dotenv()
    setup_monitor_logging(verbose=args.verbose, debug=args.debug)

    try:
        script = _create_script(args.config)
        script.run()
    except ConfigLoadingFailed as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        message = f"Monitor error: {e}"
        print(message)
        logging.getLogger(__name__).error(message)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
