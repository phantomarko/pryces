import json
from pathlib import Path

import pytest

from pryces.presentation.scripts.config import ConfigManager
from pryces.presentation.scripts.exceptions import ConfigLoadingFailed


class TestConfigManager:

    def test_raises_config_loading_failed_when_file_not_found(self, tmp_path):
        manager = ConfigManager(tmp_path / "nonexistent.json")

        with pytest.raises(ConfigLoadingFailed, match="config file not found"):
            manager.load_monitor_stocks_config()

    def test_raises_config_loading_failed_when_invalid_json(self, tmp_path):
        config_file = tmp_path / "config.json"
        config_file.write_text("not valid json")
        manager = ConfigManager(config_file)

        with pytest.raises(ConfigLoadingFailed, match="invalid config file"):
            manager.load_monitor_stocks_config()

    def test_raises_config_loading_failed_when_fields_are_invalid(self, tmp_path):
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({"duration": 0, "interval": 5, "symbols": ["AAPL"]}))
        manager = ConfigManager(config_file)

        with pytest.raises(ConfigLoadingFailed, match="invalid config file"):
            manager.load_monitor_stocks_config()

    def test_raises_config_loading_failed_on_unexpected_error(self, tmp_path, monkeypatch):
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({"duration": 1, "interval": 5, "symbols": ["AAPL"]}))
        manager = ConfigManager(config_file)
        monkeypatch.setattr(
            "pryces.presentation.scripts.config.json.loads",
            lambda _: (_ for _ in ()).throw(RuntimeError("boom")),
        )

        with pytest.raises(ConfigLoadingFailed, match="unexpected error loading config"):
            manager.load_monitor_stocks_config()

    def test_returns_valid_config_on_well_formed_file(self, tmp_path):
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps({"duration": 10, "interval": 30, "symbols": ["AAPL", "MSFT"]})
        )
        manager = ConfigManager(config_file)

        config = manager.load_monitor_stocks_config()

        assert config.duration == 10
        assert config.interval == 30
        assert config.symbols == ["AAPL", "MSFT"]
