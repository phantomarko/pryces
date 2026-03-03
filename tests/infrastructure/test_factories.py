import pytest

from pryces.infrastructure.exceptions import ConfigurationError
from pryces.infrastructure.factories import SettingsFactory


class TestCreateYahooFinanceSettings:
    def test_happy_path(self, monkeypatch):
        monkeypatch.setenv("MAX_FETCH_WORKERS", "4")
        settings = SettingsFactory.create_yahoo_finance_settings()
        assert settings.max_workers == 4
        assert settings.extra_delay_in_minutes == 0

    def test_passes_extra_delay_through(self, monkeypatch):
        monkeypatch.setenv("MAX_FETCH_WORKERS", "2")
        settings = SettingsFactory.create_yahoo_finance_settings(extra_delay_in_minutes=5)
        assert settings.extra_delay_in_minutes == 5

    def test_missing_env_var_raises_configuration_error(self, monkeypatch):
        monkeypatch.delenv("MAX_FETCH_WORKERS", raising=False)
        with pytest.raises(ConfigurationError):
            SettingsFactory.create_yahoo_finance_settings()

    def test_non_integer_env_var_raises_configuration_error(self, monkeypatch):
        monkeypatch.setenv("MAX_FETCH_WORKERS", "not-a-number")
        with pytest.raises(ConfigurationError):
            SettingsFactory.create_yahoo_finance_settings()


class TestCreateTelegramSettings:
    def test_happy_path(self, monkeypatch):
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token123")
        monkeypatch.setenv("TELEGRAM_GROUP_ID", "group456")
        settings = SettingsFactory.create_telegram_settings()
        assert settings.bot_token == "token123"
        assert settings.group_id == "group456"

    def test_missing_bot_token_raises_configuration_error(self, monkeypatch):
        monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
        monkeypatch.setenv("TELEGRAM_GROUP_ID", "group456")
        with pytest.raises(ConfigurationError):
            SettingsFactory.create_telegram_settings()

    def test_missing_group_id_raises_configuration_error(self, monkeypatch):
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token123")
        monkeypatch.delenv("TELEGRAM_GROUP_ID", raising=False)
        with pytest.raises(ConfigurationError):
            SettingsFactory.create_telegram_settings()
