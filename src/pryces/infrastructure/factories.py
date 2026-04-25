import os

from .exceptions import ConfigurationError
from .logging import (
    BOT_ENTRY_POINT,
    CLI_ENTRY_POINT,
    MONITOR_ENTRY_POINT,
    REPORT_ENTRY_POINT,
    LoggingSettings,
)
from .providers import YahooFinanceSettings
from .senders import TelegramSettings


class SettingsFactory:
    @staticmethod
    def create_yahoo_finance_settings(extra_delay_in_minutes: int = 0) -> YahooFinanceSettings:
        try:
            return YahooFinanceSettings(
                max_workers=int(os.environ["MAX_FETCH_WORKERS"]),
                extra_delay_in_minutes=extra_delay_in_minutes,
            )
        except KeyError as e:
            raise ConfigurationError(f"Missing required environment variable: {e}") from e
        except ValueError as e:
            raise ConfigurationError(
                f"Invalid value for MAX_FETCH_WORKERS: '{os.environ.get('MAX_FETCH_WORKERS')}'"
                f" — expected an integer"
            ) from e

    @staticmethod
    def create_cli_logging_settings(verbose: bool = False, debug: bool = False) -> LoggingSettings:
        return LoggingSettings(
            entry_point=CLI_ENTRY_POINT,
            verbose=verbose,
            debug=debug,
            logs_directory=os.environ.get("LOGS_DIRECTORY"),
        )

    @staticmethod
    def create_monitor_logging_settings(
        verbose: bool = False, debug: bool = False
    ) -> LoggingSettings:
        return LoggingSettings(
            entry_point=MONITOR_ENTRY_POINT,
            verbose=verbose,
            debug=debug,
            logs_directory=os.environ.get("LOGS_DIRECTORY"),
        )

    @staticmethod
    def create_bot_logging_settings(verbose: bool = False, debug: bool = False) -> LoggingSettings:
        return LoggingSettings(
            entry_point=BOT_ENTRY_POINT,
            verbose=verbose,
            debug=debug,
            logs_directory=os.environ.get("LOGS_DIRECTORY"),
        )

    @staticmethod
    def create_report_logging_settings(
        verbose: bool = False, debug: bool = False
    ) -> LoggingSettings:
        return LoggingSettings(
            entry_point=REPORT_ENTRY_POINT,
            verbose=verbose,
            debug=debug,
            logs_directory=os.environ.get("LOGS_DIRECTORY"),
        )

    @staticmethod
    def create_telegram_settings() -> TelegramSettings:
        try:
            return TelegramSettings(
                bot_token=os.environ["TELEGRAM_BOT_TOKEN"],
                group_id=os.environ["TELEGRAM_GROUP_ID"],
            )
        except KeyError as e:
            raise ConfigurationError(f"Missing required environment variable: {e}") from e
