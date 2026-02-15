import os

from .implementations import TelegramSettings, YahooFinanceSettings


class SettingsFactory:
    @staticmethod
    def create_yahoo_finance_settings() -> YahooFinanceSettings:
        return YahooFinanceSettings(
            max_workers=int(os.environ["MAX_FETCH_WORKERS"]),
        )

    @staticmethod
    def create_telegram_settings() -> TelegramSettings:
        return TelegramSettings(
            bot_token=os.environ["TELEGRAM_BOT_TOKEN"],
            group_id=os.environ["TELEGRAM_GROUP_ID"],
        )
