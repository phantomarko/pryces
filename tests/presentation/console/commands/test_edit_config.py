import json
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from pryces.presentation.console.commands.edit_config import EditConfigCommand
from pryces.presentation.scripts.config import MonitorStocksConfig, SymbolConfig


def _write_config(path: Path, interval: int, symbols: list) -> None:
    data = {
        "interval": interval,
        "symbols": [{"symbol": s, "prices": []} for s in symbols],
    }
    path.write_text(json.dumps(data))


class TestEditConfigCommand:

    def setup_method(self):
        self.command = EditConfigCommand()

    def test_get_metadata(self):
        metadata = self.command.get_metadata()
        assert metadata.id == "edit_config"

    @patch("pryces.presentation.console.commands.edit_config.get_config_files")
    def test_get_input_prompts_empty_when_no_configs(self, mock_get):
        mock_get.return_value = []
        prompts = self.command.get_input_prompts()
        assert prompts == []

    @patch("pryces.presentation.console.commands.edit_config.get_config_files")
    def test_get_input_prompts_returns_three_prompts_when_configs_exist(self, mock_get, tmp_path):
        path = tmp_path / "a.json"
        path.touch()
        mock_get.return_value = [path]

        prompts = self.command.get_input_prompts()

        assert len(prompts) == 3
        assert prompts[0].key == "config_selection"
        assert prompts[1].key == "operation"
        assert prompts[2].key == "new_value"

    @patch("pryces.presentation.console.commands.edit_config.get_config_files")
    def test_execute_no_configs_returns_error(self, mock_get):
        mock_get.return_value = []
        self.command.get_input_prompts()
        result = self.command.execute()
        assert result.success is False
        assert "No configs" in result.message

    @patch("pryces.presentation.console.commands.edit_config.get_config_files")
    def test_execute_updates_interval(self, mock_get, tmp_path):
        path = tmp_path / "test.json"
        _write_config(path, 60, ["AAPL"])
        mock_get.return_value = [path]
        self.command.get_input_prompts()

        result = self.command.execute(config_selection="1", operation="1", new_value="120")

        assert result.success is True
        data = json.loads(path.read_text())
        assert data["interval"] == 120

    @patch("pryces.presentation.console.commands.edit_config.get_config_files")
    def test_execute_updates_symbols(self, mock_get, tmp_path):
        path = tmp_path / "test.json"
        _write_config(path, 60, ["AAPL"])
        mock_get.return_value = [path]
        self.command.get_input_prompts()

        result = self.command.execute(config_selection="1", operation="2", new_value="MSFT:200,210")

        assert result.success is True
        data = json.loads(path.read_text())
        symbols = {s["symbol"]: s["prices"] for s in data["symbols"]}
        assert "MSFT" in symbols
        assert symbols["MSFT"] == [200.0, 210.0]

    @patch("pryces.presentation.console.commands.edit_config.get_config_files")
    def test_execute_returns_error_for_invalid_interval(self, mock_get, tmp_path):
        path = tmp_path / "test.json"
        _write_config(path, 60, ["AAPL"])
        mock_get.return_value = [path]
        self.command.get_input_prompts()

        result = self.command.execute(config_selection="1", operation="1", new_value="abc")

        assert result.success is False

    @patch("pryces.presentation.console.commands.edit_config.get_config_files")
    def test_execute_returns_error_for_invalid_symbols(self, mock_get, tmp_path):
        path = tmp_path / "test.json"
        _write_config(path, 60, ["AAPL"])
        mock_get.return_value = [path]
        self.command.get_input_prompts()

        result = self.command.execute(config_selection="1", operation="2", new_value="")

        assert result.success is False
