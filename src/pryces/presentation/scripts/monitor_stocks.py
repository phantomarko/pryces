import argparse
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

from ...application.interfaces import LoggerFactory
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
    RetryMessageSender,
    RetrySettings,
    TelegramMessageSender,
)
from pryces.infrastructure.logging import PythonLoggerFactory, setup_monitor_logging
from .config import ConfigManager, ConfigRefresher
from .exceptions import ConfigLoadingFailed


class MonitorStocksScript:
    def __init__(
        self,
        trigger_notifications: TriggerStocksNotifications,
        config_refresher: ConfigRefresher,
        duration: int,
        logger_factory: LoggerFactory,
    ) -> None:
        self._trigger_notifications = trigger_notifications
        self._config_refresher = config_refresher
        self._duration_seconds = duration * 60
        self._logger = logger_factory.get_logger(__name__)

    def run(self) -> None:
        self._logger.info("Monitoring started.")
        self._config_refresher.log_config()
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

            if time.monotonic() - start >= self._duration_seconds:
                break

            time.sleep(self._config_refresher.config.interval)

        self._logger.info("Monitoring finished.")


class _ScriptContext:
    def __init__(self, script: MonitorStocksScript, message_sender: FireAndForgetMessageSender):
        self.script = script
        self.message_sender = message_sender


def _create_script(
    path: Path,
    duration: int,
    logger_factory: LoggerFactory,
    extra_delay_in_minutes: int = 0,
) -> _ScriptContext:
    yahoo_finance_settings = SettingsFactory.create_yahoo_finance_settings(
        extra_delay_in_minutes=extra_delay_in_minutes
    )
    provider = YahooFinanceProvider(settings=yahoo_finance_settings, logger_factory=logger_factory)
    telegram_settings = SettingsFactory.create_telegram_settings()
    telegram_sender = TelegramMessageSender(
        settings=telegram_settings, logger_factory=logger_factory
    )
    retry_sender = RetryMessageSender(
        inner=telegram_sender,
        settings=RetrySettings(max_retries=3, base_delay=1.0, backoff_factor=2.0),
        logger_factory=logger_factory,
    )
    message_sender = FireAndForgetMessageSender(inner=retry_sender, logger_factory=logger_factory)
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
    config_refresher = ConfigRefresher(config_manager, config, logger_factory)
    script = MonitorStocksScript(
        trigger_notifications=trigger_notifications,
        config_refresher=config_refresher,
        duration=duration,
        logger_factory=logger_factory,
    )
    return _ScriptContext(script=script, message_sender=message_sender)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Monitor stocks for relevant price notifications",
    )
    parser.add_argument("config", type=Path, help="Path to the JSON configuration file")
    parser.add_argument(
        "--duration",
        type=int,
        required=True,
        help="Monitoring duration in minutes",
    )
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
    logger_factory = PythonLoggerFactory()

    try:
        context = _create_script(
            args.config,
            duration=args.duration,
            logger_factory=logger_factory,
            extra_delay_in_minutes=args.extra_delay,
        )
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
        logger_factory.get_logger(__name__).error(message)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
