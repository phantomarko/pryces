import argparse
import logging
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

from ...application.dtos import TargetPriceDTO
from ...application.services import NotificationService
from ...application.use_cases.trigger_stocks_notifications import (
    TriggerStocksNotifications,
    TriggerStocksNotificationsRequest,
)
from ...application.use_cases.sync_target_prices import (
    SyncTargetPrices,
    SyncTargetPricesRequest,
)
from ...infrastructure.factories import SettingsFactory
from ...infrastructure.implementations import (
    InMemoryMarketTransitionRepository,
    InMemoryNotificationRepository,
    InMemoryStockRepository,
    InMemoryTargetPriceRepository,
    TelegramMessageSender,
    YahooFinanceProvider,
)
from pryces.infrastructure.logging import setup_monitor_logging
from .config import ConfigManager
from .exceptions import ConfigLoadingFailed


class MonitorStocksScript:
    def __init__(
        self,
        trigger_notifications: TriggerStocksNotifications,
        sync_target_prices: SyncTargetPrices,
        config_manager: ConfigManager,
    ) -> None:
        self._trigger_notifications = trigger_notifications
        self._sync_target_prices = sync_target_prices
        self._config_manager = config_manager
        self._logger = logging.getLogger(__name__)
        self._config = self._config_manager.read_monitor_stocks_config()

    def _read_config(self) -> None:
        try:
            new_config = self._config_manager.read_monitor_stocks_config()
            if new_config != self._config:
                self._config = new_config
                self._logger.info("Config refreshed.")
                self._log_config()
                self._write_target_prices()
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

    def _write_target_prices(self) -> None:
        price_targets = [
            TargetPriceDTO(symbol=s.symbol, target=price)
            for s in self._config.symbols
            for price in s.prices
        ]
        self._sync_target_prices.handle(SyncTargetPricesRequest(price_targets=price_targets))

    def run(self) -> None:
        self._logger.info("Monitoring started.")
        self._log_config()
        self._write_target_prices()
        duration_seconds = self._config.duration * 60
        start = time.monotonic()

        while True:
            self._read_config()
            request = TriggerStocksNotificationsRequest(
                symbols=[s.symbol for s in self._config.symbols]
            )
            try:
                self._trigger_notifications.handle(request)
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
    target_price_repository = InMemoryTargetPriceRepository()
    trigger_notifications = TriggerStocksNotifications(
        provider=provider,
        notification_service=notification_service,
        stock_repository=stock_repository,
        target_price_repository=target_price_repository,
    )
    sync_target_prices = SyncTargetPrices(target_price_repository)
    return MonitorStocksScript(
        trigger_notifications=trigger_notifications,
        sync_target_prices=sync_target_prices,
        config_manager=ConfigManager(path),
    )


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
