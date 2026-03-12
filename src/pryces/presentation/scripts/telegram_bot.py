import argparse
import sys

from dotenv import load_dotenv

from ...application.interfaces import LoggerFactory, MessageSender
from ...infrastructure.factories import SettingsFactory
from ...infrastructure.logging import PythonLoggerFactory, setup_logging
from ...infrastructure.receivers import TelegramUpdatePoller
from ...infrastructure.senders import TelegramMessageSender
from .bot_commands import (
    BotCommand,
    BotCommandDispatcher,
    HelpCommand,
    TargetAddCommand,
    TargetRemoveCommand,
    TargetsCommand,
)
from .config import find_config_for_symbol


class TelegramBotScript:
    def __init__(
        self,
        poller: TelegramUpdatePoller,
        message_sender: MessageSender,
        dispatcher: BotCommandDispatcher,
        group_id: str,
        logger_factory: LoggerFactory,
    ) -> None:
        self._poller = poller
        self._message_sender = message_sender
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
                            self._message_sender.send_message(reply)
                        except Exception as e:
                            self._logger.error(f"Failed to send reply: {e}")
                offset = update.update_id + 1


def _create_script(logger_factory: LoggerFactory) -> TelegramBotScript:
    telegram_settings = SettingsFactory.create_telegram_settings()
    poller = TelegramUpdatePoller(settings=telegram_settings, logger_factory=logger_factory)
    message_sender = TelegramMessageSender(
        settings=telegram_settings, logger_factory=logger_factory
    )

    targets_cmd = TargetsCommand(find_config_for_symbol)
    target_add_cmd = TargetAddCommand(find_config_for_symbol)
    target_remove_cmd = TargetRemoveCommand(find_config_for_symbol)
    commands: list[BotCommand] = [targets_cmd, target_add_cmd, target_remove_cmd]
    help_cmd = HelpCommand(commands + [HelpCommand([])])
    all_commands = commands + [help_cmd]

    dispatcher = BotCommandDispatcher(all_commands, logger_factory)
    script = TelegramBotScript(
        poller=poller,
        message_sender=message_sender,
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
