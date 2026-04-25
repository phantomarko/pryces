import argparse
import sys
from collections.abc import Callable

from dotenv import load_dotenv

from ...application.interfaces import LoggerFactory
from ...application.use_cases.trigger_stocks_statistics import (
    TriggerStocksStatistics,
    TriggerStocksStatisticsRequest,
)
from ...infrastructure.configs import CONFIGS_DIR, ConfigStore
from ...infrastructure.formatters import RegularStockStatisticsFormatter
from ...infrastructure.factories import SettingsFactory
from ...infrastructure.logging import PythonLoggerFactory, setup_logging
from ...infrastructure.providers import YahooFinanceStatisticsProvider
from ...infrastructure.senders import TelegramMessageSender


class ReportStocksStatisticsScript:
    def __init__(
        self,
        trigger_stocks_statistics: TriggerStocksStatistics,
        list_tracked_symbols: Callable[[], list[str]],
        logger_factory: LoggerFactory,
    ) -> None:
        self._trigger_stocks_statistics = trigger_stocks_statistics
        self._list_tracked_symbols = list_tracked_symbols
        self._logger = logger_factory.get_logger(__name__)

    def run(self) -> None:
        symbols = self._list_tracked_symbols()
        if not symbols:
            self._logger.info("No symbols tracked, nothing to report.")
            return

        self._logger.info(f"Triggering statistics for {len(symbols)} symbol(s): {symbols}")
        self._trigger_stocks_statistics.handle(TriggerStocksStatisticsRequest(symbols=symbols))
        self._logger.info(f"Report triggered for {len(symbols)} symbol(s).")


def _create_script(logger_factory: LoggerFactory) -> ReportStocksStatisticsScript:
    yahoo_settings = SettingsFactory.create_yahoo_finance_settings()
    statistics_provider = YahooFinanceStatisticsProvider(
        settings=yahoo_settings, logger_factory=logger_factory
    )
    telegram_settings = SettingsFactory.create_telegram_settings()
    message_sender = TelegramMessageSender(
        settings=telegram_settings, logger_factory=logger_factory
    )
    trigger_stocks_statistics = TriggerStocksStatistics(
        statistics_provider, RegularStockStatisticsFormatter(), message_sender
    )
    config_store = ConfigStore(CONFIGS_DIR)

    return ReportStocksStatisticsScript(
        trigger_stocks_statistics=trigger_stocks_statistics,
        list_tracked_symbols=config_store.list_tracked_symbols,
        logger_factory=logger_factory,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Report price statistics for all tracked symbols via Telegram",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging to stderr")
    args = parser.parse_args()

    load_dotenv()
    setup_logging(
        SettingsFactory.create_report_logging_settings(verbose=args.verbose, debug=args.debug)
    )
    logger_factory = PythonLoggerFactory()

    try:
        script = _create_script(logger_factory)
        script.run()
    except KeyboardInterrupt:
        logger_factory.get_logger(__name__).info("Report stopped by user.")
    except Exception as e:
        message = f"Report error: {e}"
        print(message)
        logger_factory.get_logger(__name__).error(message)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
