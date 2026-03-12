import logging
import sys
from dataclasses import dataclass
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

from pryces.application.interfaces import Logger, LoggerFactory

CLI_ENTRY_POINT = "cli"
MONITOR_ENTRY_POINT = "monitor"
BOT_ENTRY_POINT = "bot"


@dataclass(frozen=True)
class LoggingSettings:
    entry_point: str
    verbose: bool = False
    debug: bool = False
    logs_directory: str | None = None
    max_bytes: int = 5 * 1024 * 1024
    backup_count: int = 3


def setup_logging(settings: LoggingSettings) -> None:
    level = logging.DEBUG if settings.debug else logging.INFO
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    if settings.debug:
        logging.getLogger("pryces").setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    if settings.verbose:
        stream_handler = logging.StreamHandler(sys.stderr)
        stream_handler.setLevel(level)
        stream_handler.setFormatter(formatter)
        root_logger.addHandler(stream_handler)

    if settings.logs_directory and Path(settings.logs_directory).is_dir():
        filename = datetime.now().strftime(f"pryces_{settings.entry_point}_%Y%m%d_%H%M%S.log")
        file_handler = RotatingFileHandler(
            Path(settings.logs_directory) / filename,
            maxBytes=settings.max_bytes,
            backupCount=settings.backup_count,
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    if not root_logger.handlers:
        root_logger.addHandler(logging.NullHandler())


class PythonLogger(Logger):
    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger

    def debug(self, message: str) -> None:
        self._logger.debug(message)

    def info(self, message: str) -> None:
        self._logger.info(message)

    def warning(self, message: str) -> None:
        self._logger.warning(message)

    def error(self, message: str) -> None:
        self._logger.error(message)


class PythonLoggerFactory(LoggerFactory):
    def get_logger(self, name: str) -> Logger:
        return PythonLogger(logging.getLogger(name))
