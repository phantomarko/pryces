import logging
import os
import sys
from datetime import datetime
from pathlib import Path


class LogFactory:
    @staticmethod
    def create(name: str) -> logging.Logger:
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)

        logger = logging.getLogger(name)

        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        stream_handler = logging.StreamHandler(sys.stderr)
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(formatter)
        root_logger.addHandler(stream_handler)

        logs_directory = os.environ.get("LOGS_DIRECTORY")
        if logs_directory and Path(logs_directory).is_dir():
            filename = datetime.now().strftime("pryces_%Y%m%d_%H%M%S.log")
            file_handler = logging.FileHandler(Path(logs_directory) / filename)
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

        return logger
