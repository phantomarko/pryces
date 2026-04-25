import pytest

from pryces.infrastructure.configs import ConfigStore
from pryces.presentation.console.commands.delete_config import DeleteConfigCommand


class TestDeleteConfigCommand:

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        self.tmp_path = tmp_path
        self.command = DeleteConfigCommand(ConfigStore(tmp_path))

    def test_get_metadata(self):
        metadata = self.command.get_metadata()
        assert metadata.id == "delete_config"

    def test_get_input_prompts_empty_when_no_configs(self):
        assert self.command.get_input_prompts() == []

    def test_get_input_prompts_returns_two_prompts_when_configs_exist(self):
        (self.tmp_path / "a.json").touch()

        prompts = self.command.get_input_prompts()

        assert len(prompts) == 2
        assert prompts[0].key == "config_selection"
        assert prompts[1].key == "confirm"

    def test_execute_no_configs_returns_error(self):
        self.command.get_input_prompts()
        result = self.command.execute()
        assert result.success is False

    def test_execute_cancels_when_not_confirmed(self):
        path = self.tmp_path / "test.json"
        path.write_text("{}")
        self.command.get_input_prompts()

        result = self.command.execute(config_selection="1", confirm="no")

        assert "cancel" in result.message.lower()
        assert path.exists()

    def test_execute_deletes_file_when_confirmed(self):
        path = self.tmp_path / "test.json"
        path.write_text("{}")
        self.command.get_input_prompts()

        result = self.command.execute(config_selection="1", confirm="yes")

        assert result.success is True
        assert not path.exists()
        assert "test.json" in result.message

    def test_execute_confirm_case_insensitive(self):
        path = self.tmp_path / "test.json"
        path.write_text("{}")
        self.command.get_input_prompts()

        result = self.command.execute(config_selection="1", confirm="YES")

        assert not path.exists()
