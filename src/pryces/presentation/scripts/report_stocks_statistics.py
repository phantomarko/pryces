import argparse
import sys

from dotenv import load_dotenv

from ...application.interfaces import LoggerFactory
from ...application.use_cases.get_stocks_statistics import (
    GetStocksStatistics,
    GetStocksStatisticsRequest,
)
from ...application.use_cases.send_messages import SendMessages, SendMessagesRequest
from ...infrastructure.factories import SettingsFactory
from ...infrastructure.logging import PythonLoggerFactory, setup_logging
from ...infrastructure.providers import YahooFinanceStatisticsProvider
from ...infrastructure.senders import TelegramMessageSender
from .config import get_all_tracked_symbols
from .formatters import format_stats


class ReportStocksStatisticsScript:
    def __init__(
        self,
        get_stocks_statistics: GetStocksStatistics,
        send_messages: SendMessages,
        logger_factory: LoggerFactory,
    ) -> None:
        self._get_stocks_statistics = get_stocks_statistics
        self._send_messages = send_messages
        self._logger = logger_factory.get_logger(__name__)

    def run(self) -> None:
        symbols = get_all_tracked_symbols()
        if not symbols:
            self._logger.info("No symbols tracked, nothing to report.")
            return

        self._logger.info(f"Fetching statistics for {len(symbols)} symbol(s): {symbols}")
        stats = self._get_stocks_statistics.handle(GetStocksStatisticsRequest(symbols=symbols))

        messages = [format_stats(dto) for dto in stats]
        result = self._send_messages.handle(SendMessagesRequest(messages=messages))
        self._logger.info(f"Report sent: {result.successful} ok, {result.failed} failed.")


def _create_script(logger_factory: LoggerFactory) -> ReportStocksStatisticsScript:
    yahoo_settings = SettingsFactory.create_yahoo_finance_settings()
    statistics_provider = YahooFinanceStatisticsProvider(
        settings=yahoo_settings, logger_factory=logger_factory
    )
    get_stocks_statistics = GetStocksStatistics(statistics_provider)

    telegram_settings = SettingsFactory.create_telegram_settings()
    message_sender = TelegramMessageSender(
        settings=telegram_settings, logger_factory=logger_factory
    )
    send_messages = SendMessages(message_sender)

    return ReportStocksStatisticsScript(
        get_stocks_statistics=get_stocks_statistics,
        send_messages=send_messages,
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
        SettingsFactory.create_bot_logging_settings(verbose=args.verbose, debug=args.debug)
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
