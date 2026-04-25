import json
from decimal import Decimal

import pytest

from pryces.infrastructure.configs import (
    ConfigManager,
    ConfigStore,
    MonitorStocksConfig,
    SymbolConfig,
)
from pryces.infrastructure.exceptions import ConfigLoadingFailed


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
            "pryces.infrastructure.configs.json.loads",
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


class TestConfigManagerMutators:

    def _write(self, path, config):
        ConfigManager(path).write_monitor_stocks_config(config)

    def test_replace_symbol_prices_overwrites_only_target_symbol(self, tmp_path):
        path = tmp_path / "c.json"
        self._write(
            path,
            MonitorStocksConfig(
                interval=30,
                symbols=[
                    SymbolConfig("AAPL", [Decimal("150")]),
                    SymbolConfig("MSFT", [Decimal("300")]),
                ],
            ),
        )

        ConfigManager(path).replace_symbol_prices("AAPL", [Decimal("200"), Decimal("210")])

        restored = ConfigManager(path).read_monitor_stocks_config()
        assert restored.symbols == [
            SymbolConfig("AAPL", [Decimal("200"), Decimal("210")]),
            SymbolConfig("MSFT", [Decimal("300")]),
        ]

    def test_replace_symbol_prices_with_empty_list_keeps_symbol_entry(self, tmp_path):
        path = tmp_path / "c.json"
        self._write(
            path,
            MonitorStocksConfig(
                interval=30,
                symbols=[SymbolConfig("AAPL", [Decimal("150")])],
            ),
        )

        ConfigManager(path).replace_symbol_prices("AAPL", [])

        restored = ConfigManager(path).read_monitor_stocks_config()
        assert restored.symbols == [SymbolConfig("AAPL", [])]

    def test_add_symbol_appends_with_empty_prices(self, tmp_path):
        path = tmp_path / "c.json"
        self._write(
            path,
            MonitorStocksConfig(
                interval=30,
                symbols=[SymbolConfig("AAPL", [Decimal("150")])],
            ),
        )

        ConfigManager(path).add_symbol("MSFT")

        restored = ConfigManager(path).read_monitor_stocks_config()
        assert restored.symbols == [
            SymbolConfig("AAPL", [Decimal("150")]),
            SymbolConfig("MSFT", []),
        ]

    def test_remove_symbol_drops_matching_entry(self, tmp_path):
        path = tmp_path / "c.json"
        self._write(
            path,
            MonitorStocksConfig(
                interval=30,
                symbols=[
                    SymbolConfig("AAPL", [Decimal("150")]),
                    SymbolConfig("MSFT", [Decimal("300")]),
                ],
            ),
        )

        ConfigManager(path).remove_symbol("AAPL")

        restored = ConfigManager(path).read_monitor_stocks_config()
        assert restored.symbols == [SymbolConfig("MSFT", [Decimal("300")])]


class TestConfigStoreListPaths:

    def test_returns_empty_when_directory_does_not_exist(self, tmp_path):
        store = ConfigStore(tmp_path / "nonexistent")
        assert store.list_paths() == []

    def test_returns_sorted_json_files(self, tmp_path):
        (tmp_path / "b.json").touch()
        (tmp_path / "a.json").touch()
        (tmp_path / "c.txt").touch()
        store = ConfigStore(tmp_path)

        result = store.list_paths()

        assert [p.name for p in result] == ["a.json", "b.json"]

    def test_excludes_non_json_files(self, tmp_path):
        (tmp_path / "config.yaml").touch()
        (tmp_path / "config.json").touch()
        store = ConfigStore(tmp_path)

        result = store.list_paths()

        assert [p.name for p in result] == ["config.json"]


class TestConfigStoreListNames:

    def test_returns_sorted_stems(self, tmp_path):
        (tmp_path / "b.json").touch()
        (tmp_path / "a.json").touch()
        store = ConfigStore(tmp_path)

        assert store.list_names() == ["a", "b"]

    def test_returns_empty_when_directory_missing(self, tmp_path):
        store = ConfigStore(tmp_path / "missing")
        assert store.list_names() == []


class TestConfigStoreFindByName:

    def test_returns_path_and_config_when_present(self, tmp_path):
        (tmp_path / "x.json").write_text(json.dumps(make_config_data()))
        store = ConfigStore(tmp_path)

        result = store.find_by_name("x")

        assert result is not None
        path, config = result
        assert path.name == "x.json"
        assert config.interval == 30

    def test_returns_none_when_directory_missing(self, tmp_path):
        store = ConfigStore(tmp_path / "missing")
        assert store.find_by_name("x") is None

    def test_returns_none_when_load_fails(self, tmp_path):
        (tmp_path / "x.json").write_text("not json")
        store = ConfigStore(tmp_path)
        assert store.find_by_name("x") is None

    def test_returns_none_when_name_unknown(self, tmp_path):
        store = ConfigStore(tmp_path)
        assert store.find_by_name("nope") is None


class TestConfigStoreFindForSymbol:

    def test_returns_first_config_alphabetically_containing_symbol(self, tmp_path):
        (tmp_path / "b.json").write_text(
            json.dumps({"interval": 30, "symbols": [{"symbol": "AAPL", "prices": []}]})
        )
        (tmp_path / "a.json").write_text(
            json.dumps({"interval": 30, "symbols": [{"symbol": "MSFT", "prices": []}]})
        )
        store = ConfigStore(tmp_path)

        result = store.find_for_symbol("AAPL")

        assert result is not None
        path, _ = result
        assert path.name == "b.json"

    def test_uppercases_symbol(self, tmp_path):
        (tmp_path / "x.json").write_text(
            json.dumps({"interval": 30, "symbols": [{"symbol": "AAPL", "prices": []}]})
        )
        store = ConfigStore(tmp_path)

        assert store.find_for_symbol("aapl") is not None

    def test_returns_none_when_no_match(self, tmp_path):
        (tmp_path / "x.json").write_text(
            json.dumps({"interval": 30, "symbols": [{"symbol": "AAPL", "prices": []}]})
        )
        store = ConfigStore(tmp_path)
        assert store.find_for_symbol("MSFT") is None

    def test_skips_malformed_files(self, tmp_path):
        (tmp_path / "bad.json").write_text("garbage")
        (tmp_path / "good.json").write_text(
            json.dumps({"interval": 30, "symbols": [{"symbol": "AAPL", "prices": []}]})
        )
        store = ConfigStore(tmp_path)

        result = store.find_for_symbol("AAPL")

        assert result is not None
        assert result[0].name == "good.json"


class TestConfigStoreListTrackedSymbols:

    def test_collects_symbols_from_multiple_configs(self, tmp_path):
        (tmp_path / "a.json").write_text(
            json.dumps({"interval": 30, "symbols": [{"symbol": "AAPL", "prices": []}]})
        )
        (tmp_path / "b.json").write_text(
            json.dumps({"interval": 30, "symbols": [{"symbol": "MSFT", "prices": []}]})
        )
        store = ConfigStore(tmp_path)

        assert store.list_tracked_symbols() == ["AAPL", "MSFT"]

    def test_returns_empty_list_when_no_configs(self, tmp_path):
        store = ConfigStore(tmp_path)
        assert store.list_tracked_symbols() == []

    def test_skips_malformed_configs(self, tmp_path):
        (tmp_path / "good.json").write_text(
            json.dumps({"interval": 30, "symbols": [{"symbol": "AAPL", "prices": []}]})
        )
        (tmp_path / "bad.json").write_text("not json")
        store = ConfigStore(tmp_path)

        assert store.list_tracked_symbols() == ["AAPL"]

    def test_deduplicates_and_sorts_symbols(self, tmp_path):
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
        store = ConfigStore(tmp_path)

        assert store.list_tracked_symbols() == ["AAPL", "MSFT"]

    def test_returns_empty_list_when_directory_does_not_exist(self, tmp_path):
        store = ConfigStore(tmp_path / "nonexistent")
        assert store.list_tracked_symbols() == []


class TestConfigStoreListTrackedSymbolsWithTargets:

    def test_collects_symbols_with_targets(self, tmp_path):
        (tmp_path / "a.json").write_text(
            json.dumps(
                {
                    "interval": 30,
                    "symbols": [{"symbol": "AAPL", "prices": [150, 200.5]}],
                }
            )
        )
        (tmp_path / "b.json").write_text(
            json.dumps(
                {
                    "interval": 30,
                    "symbols": [{"symbol": "MSFT", "prices": []}],
                }
            )
        )
        store = ConfigStore(tmp_path)

        result = store.list_tracked_symbols_with_targets()

        assert result == [
            ("AAPL", [Decimal("150"), Decimal("200.5")]),
            ("MSFT", []),
        ]

    def test_deduplicates_first_config_wins(self, tmp_path):
        (tmp_path / "a.json").write_text(
            json.dumps(
                {
                    "interval": 30,
                    "symbols": [{"symbol": "AAPL", "prices": [100]}],
                }
            )
        )
        (tmp_path / "b.json").write_text(
            json.dumps(
                {
                    "interval": 30,
                    "symbols": [{"symbol": "AAPL", "prices": [200]}],
                }
            )
        )
        store = ConfigStore(tmp_path)

        assert store.list_tracked_symbols_with_targets() == [("AAPL", [Decimal("100")])]

    def test_returns_empty_list_when_no_configs(self, tmp_path):
        store = ConfigStore(tmp_path)
        assert store.list_tracked_symbols_with_targets() == []

    def test_returns_empty_list_when_directory_does_not_exist(self, tmp_path):
        store = ConfigStore(tmp_path / "nonexistent")
        assert store.list_tracked_symbols_with_targets() == []

    def test_skips_malformed_configs(self, tmp_path):
        (tmp_path / "good.json").write_text(
            json.dumps(
                {
                    "interval": 30,
                    "symbols": [{"symbol": "AAPL", "prices": [150]}],
                }
            )
        )
        (tmp_path / "bad.json").write_text("not json")
        store = ConfigStore(tmp_path)

        assert store.list_tracked_symbols_with_targets() == [("AAPL", [Decimal("150")])]


class TestConfigStoreValidateName:

    def test_accepts_valid_name(self, tmp_path):
        store = ConfigStore(tmp_path)
        assert store.validate_name("portfolio") is None

    def test_rejects_empty(self, tmp_path):
        store = ConfigStore(tmp_path)
        assert store.validate_name("") is not None
        assert store.validate_name("   ") is not None

    def test_rejects_name_with_dot(self, tmp_path):
        store = ConfigStore(tmp_path)
        assert store.validate_name("my.config") is not None

    def test_rejects_name_with_slash(self, tmp_path):
        store = ConfigStore(tmp_path)
        assert store.validate_name("dir/name") is not None

    def test_rejects_existing_file(self, tmp_path):
        (tmp_path / "portfolio.json").touch()
        store = ConfigStore(tmp_path)
        assert store.validate_name("portfolio") is not None


class TestConfigStoreCreate:

    def test_creates_json_file_under_configs_dir(self, tmp_path):
        store = ConfigStore(tmp_path)
        config = MonitorStocksConfig(
            interval=60,
            symbols=[SymbolConfig("AAPL", [Decimal("150")])],
        )

        path = store.create("portfolio", config)

        assert path == tmp_path / "portfolio.json"
        assert path.exists()
        saved = json.loads(path.read_text())
        assert saved["interval"] == 60

    def test_creates_directory_if_missing(self, tmp_path):
        store = ConfigStore(tmp_path / "new_dir")
        config = MonitorStocksConfig(interval=30, symbols=[SymbolConfig("AAPL", [])])

        path = store.create("a", config)

        assert path.exists()
        assert path.parent == tmp_path / "new_dir"

    def test_strips_name_whitespace(self, tmp_path):
        store = ConfigStore(tmp_path)
        config = MonitorStocksConfig(interval=30, symbols=[SymbolConfig("AAPL", [])])

        path = store.create("  portfolio  ", config)

        assert path.name == "portfolio.json"


class TestConfigStoreDeleteByPath:

    def test_removes_file(self, tmp_path):
        path = tmp_path / "portfolio.json"
        path.write_text("{}")
        store = ConfigStore(tmp_path)

        store.delete_by_path(path)

        assert not path.exists()
