import argparse
import sys

from dotenv import load_dotenv

from ...application.dtos import StockStatisticsDTO
from ...application.interfaces import LoggerFactory
from ...application.use_cases.get_stocks_statistics import (
    GetStocksStatistics,
    GetStocksStatisticsRequest,
)
from ...application.use_cases.send_messages import SendMessages, SendMessagesRequest
from ...infrastructure.factories import SettingsFactory
from ...infrastructure.logging import PythonLoggerFactory, setup_logging
from ...infrastructure.providers import YahooFinanceStatisticsProvider
from ...infrastructure.receivers import TelegramUpdatePoller
from ...infrastructure.senders import TelegramMessageSender
from .bot_commands import (
    BotCommand,
    BotCommandDispatcher,
    ConfigsCommand,
    HelpCommand,
    StatsCommand,
    SymbolAddCommand,
    SymbolRemoveCommand,
    SymbolsCommand,
    TargetAddCommand,
    TargetRemoveCommand,
    TargetsCommand,
)
from .config import (
    find_config_by_name,
    find_config_for_symbol,
    get_all_tracked_symbols_with_targets,
    get_config_names,
)


class TelegramBotScript:
    def __init__(
        self,
        poller: TelegramUpdatePoller,
        send_messages: SendMessages,
        dispatcher: BotCommandDispatcher,
        group_id: str,
        logger_factory: LoggerFactory,
    ) -> None:
        self._poller = poller
        self._send_messages = send_messages
        self._dispatcher = dispatcher
        self._group_id = group_id
        self._logger = logger_factory.get_logger(__name__)

    def run(self) -> None:
        self._logger.info("Telegram bot started.")
        offset = 0

        while True:
            updates = self._poller.get_updates(offset)
            for update in updates:
                if update.chat_id == self._group_id:
                    reply = self._dispatcher.dispatch(update.text)
                    if reply:
                        try:
                            self._send_messages.handle(SendMessagesRequest(messages=[reply]))
                        except Exception as e:
                            self._logger.error(f"Failed to send reply: {e}")
                offset = update.update_id + 1


def _create_script(logger_factory: LoggerFactory) -> TelegramBotScript:
    telegram_settings = SettingsFactory.create_telegram_settings()
    poller = TelegramUpdatePoller(settings=telegram_settings, logger_factory=logger_factory)
    telegram_message_sender = TelegramMessageSender(
        settings=telegram_settings, logger_factory=logger_factory
    )
    send_messages = SendMessages(telegram_message_sender)

    yahoo_settings = SettingsFactory.create_yahoo_finance_settings()
    statistics_provider = YahooFinanceStatisticsProvider(
        settings=yahoo_settings, logger_factory=logger_factory
    )
    get_stocks_statistics = GetStocksStatistics(statistics_provider)

    def get_stock_statistics(symbol: str) -> StockStatisticsDTO | None:
        results = get_stocks_statistics.handle(GetStocksStatisticsRequest(symbols=[symbol]))
        return results[0] if results else None

    targets_cmd = TargetsCommand(find_config_for_symbol)
    target_add_cmd = TargetAddCommand(find_config_for_symbol)
    target_remove_cmd = TargetRemoveCommand(find_config_for_symbol)
    symbols_cmd = SymbolsCommand(get_all_tracked_symbols_with_targets)
    configs_cmd = ConfigsCommand(get_config_names)
    symbol_add_cmd = SymbolAddCommand(find_config_by_name)
    symbol_remove_cmd = SymbolRemoveCommand(find_config_for_symbol)
    stats_cmd = StatsCommand(get_stock_statistics)
    commands: list[BotCommand] = [
        configs_cmd,
        symbols_cmd,
        symbol_add_cmd,
        symbol_remove_cmd,
        targets_cmd,
        target_add_cmd,
        target_remove_cmd,
        stats_cmd,
    ]
    help_cmd = HelpCommand(commands + [HelpCommand([])])
    all_commands = commands + [help_cmd]

    dispatcher = BotCommandDispatcher(all_commands, logger_factory)
    script = TelegramBotScript(
        poller=poller,
        send_messages=send_messages,
        dispatcher=dispatcher,
        group_id=telegram_settings.group_id,
        logger_factory=logger_factory,
    )
    return script


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Telegram bot for managing target prices",
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
        logger_factory.get_logger(__name__).info("Bot stopped by user.")
    except Exception as e:
        message = f"Bot error: {e}"
        print(message)
        logger_factory.get_logger(__name__).error(message)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
