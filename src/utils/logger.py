import logging
import sys

def setup_logger(name: str) -> logging.Logger:
    """Creates and configures a simple console logger."""
    logger = logging.getLogger(name)

    # Prevent duplicate log handlers if setup_logger() is called multiple times
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('[%(levelname)s] %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger
