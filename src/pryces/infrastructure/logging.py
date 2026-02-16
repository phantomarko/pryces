import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

CLI_ENTRY_POINT = "cli"
MONITOR_ENTRY_POINT = "monitor"


def _setup_logger(entry_point: str, verbose: bool = False, debug: bool = False) -> None:
    level = logging.DEBUG if debug else logging.INFO
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    if debug:
        logging.getLogger("pryces").setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    if verbose:
        stream_handler = logging.StreamHandler(sys.stderr)
        stream_handler.setLevel(level)
        stream_handler.setFormatter(formatter)
        root_logger.addHandler(stream_handler)

    logs_directory = os.environ.get("LOGS_DIRECTORY")
    if logs_directory and Path(logs_directory).is_dir():
        filename = datetime.now().strftime(f"pryces_{entry_point}_%Y%m%d_%H%M%S.log")
        file_handler = RotatingFileHandler(
            Path(logs_directory) / filename,
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    if not root_logger.handlers:
        root_logger.addHandler(logging.NullHandler())


def setup_cli_logging(verbose: bool = False, debug: bool = False) -> None:
    _setup_logger(CLI_ENTRY_POINT, verbose=verbose, debug=debug)


def setup_monitor_logging(verbose: bool = False, debug: bool = False) -> None:
    _setup_logger(MONITOR_ENTRY_POINT, verbose=verbose, debug=debug)
