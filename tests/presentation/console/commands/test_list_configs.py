from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

import pytest

from pryces.presentation.console.commands.list_configs import ListConfigsCommand
from pryces.presentation.scripts.config import MonitorStocksConfig, SymbolConfig


class TestListConfigsCommand:

    def setup_method(self):
        self.command = ListConfigsCommand()

    def test_get_metadata(self):
        metadata = self.command.get_metadata()
        assert metadata.id == "list_configs"
        assert metadata.name == "List Configs"

    def test_get_input_prompts_returns_empty(self):
        assert self.command.get_input_prompts() == []

    @patch("pryces.presentation.console.commands.list_configs.get_config_files")
    def test_execute_no_configs(self, mock_get):
        mock_get.return_value = []
        result = self.command.execute()
        assert "No configs found" in result.message

    @patch("pryces.presentation.console.commands.list_configs.ConfigManager")
    @patch("pryces.presentation.console.commands.list_configs.get_config_files")
    def test_execute_shows_config_details(self, mock_get, mock_manager_cls, tmp_path):
        path = tmp_path / "portfolio.json"
        path.touch()
        mock_get.return_value = [path]

        config = MonitorStocksConfig(
            interval=60,
            symbols=[SymbolConfig(symbol="AAPL", prices=[Decimal("150")])],
        )
        mock_manager_cls.return_value.read_monitor_stocks_config.return_value = config

        result = self.command.execute()

        assert "portfolio.json" in result.message
        assert "60" in result.message
        assert "AAPL" in result.message

    @patch("pryces.presentation.console.commands.list_configs.ConfigManager")
    @patch("pryces.presentation.console.commands.list_configs.get_config_files")
    def test_execute_handles_load_error(self, mock_get, mock_manager_cls, tmp_path):
        path = tmp_path / "broken.json"
        path.touch()
        mock_get.return_value = [path]
        mock_manager_cls.return_value.read_monitor_stocks_config.side_effect = Exception("bad file")

        result = self.command.execute()

        assert "broken.json" in result.message
        assert "error" in result.message.lower()
