import logging
from unittest.mock import MagicMock, patch

from pryces.infrastructure.logging import PythonLogger, PythonLoggerFactory


class TestPythonLogger:
    def setup_method(self):
        self.inner = MagicMock(spec=logging.Logger)
        self.logger = PythonLogger(self.inner)

    def test_debug_delegates_to_inner(self):
        self.logger.debug("debug msg")

        self.inner.debug.assert_called_once_with("debug msg")

    def test_info_delegates_to_inner(self):
        self.logger.info("info msg")

        self.inner.info.assert_called_once_with("info msg")

    def test_warning_delegates_to_inner(self):
        self.logger.warning("warning msg")

        self.inner.warning.assert_called_once_with("warning msg")

    def test_error_delegates_to_inner(self):
        self.logger.error("error msg")

        self.inner.error.assert_called_once_with("error msg")


class TestPythonLoggerFactory:
    def test_get_logger_returns_python_logger_instance(self):
        factory = PythonLoggerFactory()

        result = factory.get_logger("some.module")

        assert isinstance(result, PythonLogger)

    def test_get_logger_wraps_correct_logger(self):
        factory = PythonLoggerFactory()

        with patch("pryces.infrastructure.logging.logging.getLogger") as mock_get:
            mock_get.return_value = MagicMock(spec=logging.Logger)
            factory.get_logger("my.module")

        mock_get.assert_called_once_with("my.module")
