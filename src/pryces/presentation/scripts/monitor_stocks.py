import argparse
import logging
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

from ...application.services import DelayWindowChecker, NotificationService, StockSynchronizer
from ...application.use_cases.trigger_stocks_notifications import (
    TriggerStocksNotifications,
    TriggerStocksNotificationsRequest,
)
from ...infrastructure.factories import SettingsFactory
from ...infrastructure.providers import YahooFinanceProvider
from ...infrastructure.repositories import (
    InMemoryMarketTransitionRepository,
    InMemoryStockRepository,
)
from ...infrastructure.senders import (
    FireAndForgetMessageSender,
    TelegramMessageSender,
)
from pryces.infrastructure.logging import setup_monitor_logging
from .config import ConfigManager, ConfigRefresher
from .exceptions import ConfigLoadingFailed


class MonitorStocksScript:
    def __init__(
        self,
        trigger_notifications: TriggerStocksNotifications,
        config_refresher: ConfigRefresher,
    ) -> None:
        self._trigger_notifications = trigger_notifications
        self._config_refresher = config_refresher
        self._logger = logging.getLogger(__name__)

    def run(self) -> None:
        self._logger.info("Monitoring started.")
        self._config_refresher.log_config()
        config = self._config_refresher.config
        duration_seconds = config.duration * 60
        start = time.monotonic()

        while True:
            self._config_refresher.refresh()
            config = self._config_refresher.config
            request = TriggerStocksNotificationsRequest(
                symbols=[s.symbol for s in config.symbols],
                targets={s.symbol: s.prices for s in config.symbols},
            )
            try:
                fulfilled = self._trigger_notifications.handle(request)
                self._config_refresher.remove_fulfilled_targets(fulfilled)
            except Exception as e:
                self._logger.warning(f"Exception caught: {e}")

            if time.monotonic() - start >= duration_seconds:
                break

            time.sleep(self._config_refresher.config.interval)

        self._logger.info("Monitoring finished.")


class _ScriptContext:
    def __init__(self, script: MonitorStocksScript, message_sender: FireAndForgetMessageSender):
        self.script = script
        self.message_sender = message_sender


def _create_script(path: Path, extra_delay_in_minutes: int = 0) -> _ScriptContext:
    yahoo_finance_settings = SettingsFactory.create_yahoo_finance_settings(
        extra_delay_in_minutes=extra_delay_in_minutes
    )
    provider = YahooFinanceProvider(settings=yahoo_finance_settings)
    telegram_settings = SettingsFactory.create_telegram_settings()
    telegram_sender = TelegramMessageSender(settings=telegram_settings)
    message_sender = FireAndForgetMessageSender(inner=telegram_sender)
    transition_repository = InMemoryMarketTransitionRepository()
    delay_window_checker = DelayWindowChecker(transition_repository)
    notification_service = NotificationService(message_sender, delay_window_checker)
    stock_repository = InMemoryStockRepository()
    stock_synchronizer = StockSynchronizer(provider=provider, stock_repository=stock_repository)
    trigger_notifications = TriggerStocksNotifications(
        stock_synchronizer=stock_synchronizer,
        notification_service=notification_service,
    )
    config_manager = ConfigManager(path)
    config = config_manager.read_monitor_stocks_config()
    config_refresher = ConfigRefresher(config_manager, config)
    script = MonitorStocksScript(
        trigger_notifications=trigger_notifications,
        config_refresher=config_refresher,
    )
    return _ScriptContext(script=script, message_sender=message_sender)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Monitor stocks for relevant price notifications",
    )
    parser.add_argument("config", type=Path, help="Path to the JSON configuration file")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging to stderr")
    parser.add_argument(
        "--extra-delay",
        type=int,
        default=0,
        help="Extra delay in minutes added to the yfinance price delay (default: 0)",
    )
    args = parser.parse_args()

    load_dotenv()
    setup_monitor_logging(verbose=args.verbose, debug=args.debug)

    try:
        context = _create_script(args.config, extra_delay_in_minutes=args.extra_delay)
        try:
            context.script.run()
        finally:
            context.message_sender.shutdown()
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
