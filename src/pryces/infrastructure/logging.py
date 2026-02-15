import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup(verbose: bool = False, debug: bool = False) -> None:
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
        filename = datetime.now().strftime("pryces_%Y%m%d_%H%M%S.log")
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
