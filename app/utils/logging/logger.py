import sys
import logging
from app.utils.logging.formatter import ColorFormatter


def get_logger(name: str) -> logging.Logger:
    """
    Return a logger instance with colored levels and aligned formatting.
    Levels:
        - DEBUG (blue)
        - INFO (green)
        - WARNING (yellow)
        - ERROR (red)
        - CRITICAL (magenta)
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = ColorFormatter("%(levelname)s %(asctime)s - %(name)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger
