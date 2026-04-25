import json
from decimal import Decimal

import pytest

from pryces.infrastructure.configs import ConfigStore
from pryces.presentation.console.commands.list_configs import ListConfigsCommand


class TestListConfigsCommand:

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        self.tmp_path = tmp_path
        self.command = ListConfigsCommand(ConfigStore(tmp_path))

    def test_get_metadata(self):
        metadata = self.command.get_metadata()
        assert metadata.id == "list_configs"
        assert metadata.name == "List Configs"

    def test_get_input_prompts_returns_empty(self):
        assert self.command.get_input_prompts() == []

    def test_execute_no_configs(self):
        result = self.command.execute()
        assert "No configs found" in result.message

    def test_execute_shows_config_details(self):
        path = self.tmp_path / "portfolio.json"
        path.write_text(
            json.dumps({"interval": 60, "symbols": [{"symbol": "AAPL", "prices": [150]}]})
        )

        result = self.command.execute()

        assert "portfolio.json" in result.message
        assert "60" in result.message
        assert "AAPL" in result.message

    def test_execute_handles_load_error(self):
        path = self.tmp_path / "broken.json"
        path.write_text("garbage")

        result = self.command.execute()

        assert "broken.json" in result.message
        assert "error" in result.message.lower()
