import json

import pytest

from pryces.infrastructure.configs import ConfigStore
from pryces.presentation.console.commands.create_config import CreateConfigCommand


class TestCreateConfigCommandNameValidator:

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        self.command = CreateConfigCommand(ConfigStore(tmp_path))
        self.tmp_path = tmp_path

    def _get_name_validator(self):
        prompts = self.command.get_input_prompts()
        name_prompt = next(p for p in prompts if p.key == "name")
        return name_prompt.validator

    def test_accepts_valid_name(self):
        assert self._get_name_validator()("portfolio") is None

    def test_rejects_empty(self):
        validator = self._get_name_validator()
        assert validator("") is not None
        assert validator("   ") is not None

    def test_rejects_name_with_dot(self):
        assert self._get_name_validator()("my.config") is not None

    def test_rejects_name_with_slash(self):
        assert self._get_name_validator()("dir/name") is not None

    def test_rejects_existing_file(self):
        (self.tmp_path / "portfolio.json").touch()
        assert self._get_name_validator()("portfolio") is not None


class TestCreateConfigCommand:

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        self.tmp_path = tmp_path
        self.command = CreateConfigCommand(ConfigStore(tmp_path))

    def test_get_metadata(self):
        metadata = self.command.get_metadata()
        assert metadata.id == "create_config"

    def test_get_input_prompts_returns_three_prompts(self):
        prompts = self.command.get_input_prompts()
        assert len(prompts) == 3
        keys = [p.key for p in prompts]
        assert keys == ["name", "interval", "symbols"]

    def test_execute_creates_config_file(self):
        result = self.command.execute(name="test", interval="60", symbols="AAPL MSFT:150,155")

        assert result.success is True
        config_file = self.tmp_path / "test.json"
        assert config_file.exists()
        data = json.loads(config_file.read_text())
        assert data["interval"] == 60
        symbols = {s["symbol"]: s["prices"] for s in data["symbols"]}
        assert "AAPL" in symbols
        assert symbols["AAPL"] == []
        assert "MSFT" in symbols
        assert symbols["MSFT"] == [150.0, 155.0]

    def test_execute_result_includes_path(self):
        result = self.command.execute(name="test", interval="30", symbols="GOOG")
        assert "test.json" in result.message
