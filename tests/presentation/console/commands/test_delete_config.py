import json
from pathlib import Path
from unittest.mock import patch

import pytest

from pryces.presentation.console.commands.delete_config import DeleteConfigCommand

_PATCH_TARGET = "pryces.presentation.console.commands.delete_config.get_config_files"


class TestDeleteConfigCommand:

    def setup_method(self):
        self.command = DeleteConfigCommand()

    @pytest.fixture
    def mock_get_config_files(self):
        with patch(_PATCH_TARGET) as mock_get:
            yield mock_get

    def test_get_metadata(self):
        metadata = self.command.get_metadata()
        assert metadata.id == "delete_config"

    def test_get_input_prompts_empty_when_no_configs(self, mock_get_config_files):
        mock_get_config_files.return_value = []
        prompts = self.command.get_input_prompts()
        assert prompts == []

    def test_get_input_prompts_returns_two_prompts_when_configs_exist(
        self, mock_get_config_files, tmp_path
    ):
        path = tmp_path / "a.json"
        path.touch()
        mock_get_config_files.return_value = [path]

        prompts = self.command.get_input_prompts()

        assert len(prompts) == 2
        assert prompts[0].key == "config_selection"
        assert prompts[1].key == "confirm"

    def test_execute_no_configs_returns_error(self, mock_get_config_files):
        mock_get_config_files.return_value = []
        self.command.get_input_prompts()
        result = self.command.execute()
        assert result.success is False

    def test_execute_cancels_when_not_confirmed(self, mock_get_config_files, tmp_path):
        path = tmp_path / "test.json"
        path.write_text("{}")
        mock_get_config_files.return_value = [path]
        self.command.get_input_prompts()

        result = self.command.execute(config_selection="1", confirm="no")

        assert "cancel" in result.message.lower()
        assert path.exists()

    def test_execute_deletes_file_when_confirmed(self, mock_get_config_files, tmp_path):
        path = tmp_path / "test.json"
        path.write_text("{}")
        mock_get_config_files.return_value = [path]
        self.command.get_input_prompts()

        result = self.command.execute(config_selection="1", confirm="yes")

        assert result.success is True
        assert not path.exists()
        assert "test.json" in result.message

    def test_execute_confirm_case_insensitive(self, mock_get_config_files, tmp_path):
        path = tmp_path / "test.json"
        path.write_text("{}")
        mock_get_config_files.return_value = [path]
        self.command.get_input_prompts()

        result = self.command.execute(config_selection="1", confirm="YES")

        assert not path.exists()
