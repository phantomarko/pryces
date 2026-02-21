import os

from .implementations import TelegramSettings, YahooFinanceSettings


class SettingsFactory:
    @staticmethod
    def create_yahoo_finance_settings() -> YahooFinanceSettings:
        try:
            extra_delay = os.environ.get("EXTRA_DELAY_IN_MINUTES", "0") or "0"
            return YahooFinanceSettings(
                max_workers=int(os.environ["MAX_FETCH_WORKERS"]),
                extra_delay_in_minutes=int(extra_delay),
            )
        except KeyError as e:
            raise EnvironmentError(f"Missing required environment variable: {e}") from e

    @staticmethod
    def create_telegram_settings() -> TelegramSettings:
        try:
            return TelegramSettings(
                bot_token=os.environ["TELEGRAM_BOT_TOKEN"],
                group_id=os.environ["TELEGRAM_GROUP_ID"],
            )
        except KeyError as e:
            raise EnvironmentError(f"Missing required environment variable: {e}") from e
