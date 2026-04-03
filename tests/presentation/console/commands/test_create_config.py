import json
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

import pytest

from pryces.presentation.console.commands.create_config import CreateConfigCommand
from pryces.presentation.console.commands.base import InputPrompt


class TestCreateConfigCommandNameValidator:
    """Tests for the config name validation logic exposed through get_input_prompts()."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.command = CreateConfigCommand()

    def _get_name_validator(self):
        prompts = self.command.get_input_prompts()
        name_prompt = next(p for p in prompts if p.key == "name")
        return name_prompt.validator

    def test_accepts_valid_name(self, tmp_path):
        validator = self._get_name_validator()
        with patch("pryces.presentation.console.commands.create_config.CONFIGS_DIR", tmp_path):
            assert validator("portfolio") is None

    def test_rejects_empty(self, tmp_path):
        validator = self._get_name_validator()
        with patch("pryces.presentation.console.commands.create_config.CONFIGS_DIR", tmp_path):
            assert validator("") is not None
            assert validator("   ") is not None

    def test_rejects_name_with_dot(self, tmp_path):
        validator = self._get_name_validator()
        with patch("pryces.presentation.console.commands.create_config.CONFIGS_DIR", tmp_path):
            assert validator("my.config") is not None

    def test_rejects_name_with_slash(self, tmp_path):
        validator = self._get_name_validator()
        with patch("pryces.presentation.console.commands.create_config.CONFIGS_DIR", tmp_path):
            assert validator("dir/name") is not None

    def test_rejects_existing_file(self, tmp_path):
        (tmp_path / "portfolio.json").touch()
        validator = self._get_name_validator()
        with patch("pryces.presentation.console.commands.create_config.CONFIGS_DIR", tmp_path):
            assert validator("portfolio") is not None


class TestCreateConfigCommand:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.command = CreateConfigCommand()

    def test_get_metadata(self):
        metadata = self.command.get_metadata()
        assert metadata.id == "create_config"

    def test_get_input_prompts_returns_three_prompts(self):
        prompts = self.command.get_input_prompts()
        assert len(prompts) == 3
        keys = [p.key for p in prompts]
        assert keys == ["name", "interval", "symbols"]

    def test_execute_creates_config_file(self, tmp_path):
        with patch("pryces.presentation.console.commands.create_config.CONFIGS_DIR", tmp_path):
            result = self.command.execute(name="test", interval="60", symbols="AAPL MSFT:150,155")

        assert result.success is True
        config_file = tmp_path / "test.json"
        assert config_file.exists()
        data = json.loads(config_file.read_text())
        assert data["interval"] == 60
        symbols = {s["symbol"]: s["prices"] for s in data["symbols"]}
        assert "AAPL" in symbols
        assert symbols["AAPL"] == []
        assert "MSFT" in symbols
        assert symbols["MSFT"] == [150.0, 155.0]

    def test_execute_result_includes_path(self, tmp_path):
        with patch("pryces.presentation.console.commands.create_config.CONFIGS_DIR", tmp_path):
            result = self.command.execute(name="test", interval="30", symbols="GOOG")

        assert "test.json" in result.message
