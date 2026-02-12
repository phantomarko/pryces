import os

from .implementations import TelegramSettings


class SettingsFactory:
    @staticmethod
    def create_telegram_settings() -> TelegramSettings:
        return TelegramSettings(
            bot_token=os.environ["TELEGRAM_BOT_TOKEN"],
            group_id=os.environ["TELEGRAM_GROUP_ID"],
        )
