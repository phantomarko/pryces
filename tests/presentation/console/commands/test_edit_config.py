import json

import pytest

from pryces.infrastructure.configs import ConfigStore
from pryces.presentation.console.commands.edit_config import EditConfigCommand


def _write_config(path, interval, symbols):
    data = {
        "interval": interval,
        "symbols": [{"symbol": s, "prices": []} for s in symbols],
    }
    path.write_text(json.dumps(data))


class TestEditConfigCommand:

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        self.tmp_path = tmp_path
        self.command = EditConfigCommand(ConfigStore(tmp_path))

    def test_get_metadata(self):
        metadata = self.command.get_metadata()
        assert metadata.id == "edit_config"

    def test_get_input_prompts_empty_when_no_configs(self):
        assert self.command.get_input_prompts() == []

    def test_get_input_prompts_returns_three_prompts_when_configs_exist(self):
        path = self.tmp_path / "a.json"
        _write_config(path, 60, ["AAPL"])

        prompts = self.command.get_input_prompts()

        assert len(prompts) == 3
        assert prompts[0].key == "config_selection"
        assert prompts[1].key == "operation"
        assert prompts[2].key == "new_value"

    def test_execute_no_configs_returns_error(self):
        self.command.get_input_prompts()
        result = self.command.execute()
        assert result.success is False
        assert "No configs" in result.message

    def test_execute_updates_interval(self):
        path = self.tmp_path / "test.json"
        _write_config(path, 60, ["AAPL"])
        self.command.get_input_prompts()

        result = self.command.execute(config_selection="1", operation="1", new_value="120")

        assert result.success is True
        data = json.loads(path.read_text())
        assert data["interval"] == 120

    def test_execute_updates_symbols(self):
        path = self.tmp_path / "test.json"
        _write_config(path, 60, ["AAPL"])
        self.command.get_input_prompts()

        result = self.command.execute(config_selection="1", operation="2", new_value="MSFT:200,210")

        assert result.success is True
        data = json.loads(path.read_text())
        symbols = {s["symbol"]: s["prices"] for s in data["symbols"]}
        assert "MSFT" in symbols
        assert symbols["MSFT"] == [200.0, 210.0]

    def test_execute_returns_error_for_invalid_interval(self):
        path = self.tmp_path / "test.json"
        _write_config(path, 60, ["AAPL"])
        self.command.get_input_prompts()

        result = self.command.execute(config_selection="1", operation="1", new_value="abc")

        assert result.success is False

    def test_execute_returns_error_for_invalid_symbols(self):
        path = self.tmp_path / "test.json"
        _write_config(path, 60, ["AAPL"])
        self.command.get_input_prompts()

        result = self.command.execute(config_selection="1", operation="2", new_value="")

        assert result.success is False
