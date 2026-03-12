import json
from decimal import Decimal
from pathlib import Path

import pytest

from pryces.presentation.scripts.config import (
    ConfigManager,
    MonitorStocksConfig,
    SymbolConfig,
    get_all_tracked_symbols,
)
from pryces.presentation.scripts.exceptions import ConfigLoadingFailed


def make_config_data(**overrides) -> dict:
    base = {
        "interval": 30,
        "symbols": [
            {"symbol": "AAPL", "prices": [5]},
            {"symbol": "MSFT", "prices": [1, 0.92]},
        ],
    }
    base.update(overrides)
    return base


class TestConfigManager:

    def test_raises_config_loading_failed_when_file_not_found(self, tmp_path):
        manager = ConfigManager(tmp_path / "nonexistent.json")

        with pytest.raises(ConfigLoadingFailed, match="config file not found") as exc_info:
            manager.read_monitor_stocks_config()

        assert isinstance(exc_info.value.__cause__, FileNotFoundError)

    def test_raises_config_loading_failed_when_invalid_json(self, tmp_path):
        config_file = tmp_path / "config.json"
        config_file.write_text("not valid json")
        manager = ConfigManager(config_file)

        with pytest.raises(ConfigLoadingFailed, match="invalid config file") as exc_info:
            manager.read_monitor_stocks_config()

        assert isinstance(exc_info.value.__cause__, json.JSONDecodeError)

    def test_raises_config_loading_failed_when_fields_are_invalid(self, tmp_path):
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(make_config_data(interval=0)))
        manager = ConfigManager(config_file)

        with pytest.raises(ConfigLoadingFailed, match="invalid config file") as exc_info:
            manager.read_monitor_stocks_config()

        assert isinstance(exc_info.value.__cause__, ValueError)

    def test_raises_config_loading_failed_when_symbol_missing_key(self, tmp_path):
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({"interval": 5, "symbols": [{"prices": [5]}]}))
        manager = ConfigManager(config_file)

        with pytest.raises(ConfigLoadingFailed, match="invalid config file") as exc_info:
            manager.read_monitor_stocks_config()

        assert isinstance(exc_info.value.__cause__, KeyError)

    def test_raises_config_loading_failed_on_unexpected_error(self, tmp_path, monkeypatch):
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(make_config_data()))
        manager = ConfigManager(config_file)
        monkeypatch.setattr(
            "pryces.presentation.scripts.config.json.loads",
            lambda _: (_ for _ in ()).throw(RuntimeError("boom")),
        )

        with pytest.raises(
            ConfigLoadingFailed, match="unexpected error loading config"
        ) as exc_info:
            manager.read_monitor_stocks_config()

        assert isinstance(exc_info.value.__cause__, RuntimeError)

    def test_returns_valid_config_on_well_formed_file(self, tmp_path):
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(make_config_data()))
        manager = ConfigManager(config_file)

        config = manager.read_monitor_stocks_config()

        assert config.interval == 30
        assert config.symbols == [
            SymbolConfig(symbol="AAPL", prices=[Decimal("5")]),
            SymbolConfig(symbol="MSFT", prices=[Decimal("1"), Decimal("0.92")]),
        ]

    def test_parses_multiple_prices_per_symbol(self, tmp_path):
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps({"interval": 5, "symbols": [{"symbol": "HUMA", "prices": [1, 0.92]}]})
        )
        manager = ConfigManager(config_file)

        config = manager.read_monitor_stocks_config()

        assert config.symbols[0].prices == [Decimal("1"), Decimal("0.92")]

    def test_write_creates_json_file_with_config_data(self, tmp_path):
        config_file = tmp_path / "config.json"
        manager = ConfigManager(config_file)
        config = MonitorStocksConfig(
            interval=30,
            symbols=[
                SymbolConfig(symbol="AAPL", prices=[Decimal("5")]),
                SymbolConfig(symbol="MSFT", prices=[Decimal("1"), Decimal("0.92")]),
            ],
        )

        manager.write_monitor_stocks_config(config)

        saved = json.loads(config_file.read_text())
        assert saved["interval"] == 30
        assert saved["symbols"] == [
            {"symbol": "AAPL", "prices": [5.0]},
            {"symbol": "MSFT", "prices": [1.0, 0.92]},
        ]

    def test_write_reflects_removed_prices(self, tmp_path):
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(make_config_data()))
        manager = ConfigManager(config_file)
        original = manager.read_monitor_stocks_config()
        trimmed = MonitorStocksConfig(
            interval=original.interval,
            symbols=[
                SymbolConfig(symbol="MSFT", prices=[Decimal("1")]),
            ],
        )

        manager.write_monitor_stocks_config(trimmed)

        saved = json.loads(config_file.read_text())
        assert len(saved["symbols"]) == 1
        assert saved["symbols"][0] == {"symbol": "MSFT", "prices": [1.0]}

    def test_written_config_round_trips_through_read(self, tmp_path):
        config_file = tmp_path / "config.json"
        manager = ConfigManager(config_file)
        config = MonitorStocksConfig(
            interval=60,
            symbols=[SymbolConfig(symbol="HUMA", prices=[Decimal("1"), Decimal("0.92")])],
        )

        manager.write_monitor_stocks_config(config)
        restored = manager.read_monitor_stocks_config()

        assert restored.interval == config.interval
        assert restored.symbols[0].symbol == "HUMA"
        assert restored.symbols[0].prices == [Decimal("1"), Decimal("0.92")]


class TestGetAllTrackedSymbols:

    def test_collects_symbols_from_multiple_configs(self, tmp_path, monkeypatch):
        monkeypatch.setattr("pryces.presentation.scripts.config.CONFIGS_DIR", tmp_path)
        (tmp_path / "a.json").write_text(
            json.dumps({"interval": 30, "symbols": [{"symbol": "AAPL", "prices": []}]})
        )
        (tmp_path / "b.json").write_text(
            json.dumps({"interval": 30, "symbols": [{"symbol": "MSFT", "prices": []}]})
        )

        result = get_all_tracked_symbols()

        assert result == ["AAPL", "MSFT"]

    def test_returns_empty_list_when_no_configs(self, tmp_path, monkeypatch):
        monkeypatch.setattr("pryces.presentation.scripts.config.CONFIGS_DIR", tmp_path)

        result = get_all_tracked_symbols()

        assert result == []

    def test_skips_malformed_configs(self, tmp_path, monkeypatch):
        monkeypatch.setattr("pryces.presentation.scripts.config.CONFIGS_DIR", tmp_path)
        (tmp_path / "good.json").write_text(
            json.dumps({"interval": 30, "symbols": [{"symbol": "AAPL", "prices": []}]})
        )
        (tmp_path / "bad.json").write_text("not json")

        result = get_all_tracked_symbols()

        assert result == ["AAPL"]

    def test_deduplicates_and_sorts_symbols(self, tmp_path, monkeypatch):
        monkeypatch.setattr("pryces.presentation.scripts.config.CONFIGS_DIR", tmp_path)
        (tmp_path / "a.json").write_text(
            json.dumps(
                {
                    "interval": 30,
                    "symbols": [
                        {"symbol": "MSFT", "prices": []},
                        {"symbol": "AAPL", "prices": []},
                    ],
                }
            )
        )
        (tmp_path / "b.json").write_text(
            json.dumps({"interval": 30, "symbols": [{"symbol": "AAPL", "prices": []}]})
        )

        result = get_all_tracked_symbols()

        assert result == ["AAPL", "MSFT"]

    def test_returns_empty_list_when_directory_does_not_exist(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "pryces.presentation.scripts.config.CONFIGS_DIR", tmp_path / "nonexistent"
        )

        result = get_all_tracked_symbols()

        assert result == []
