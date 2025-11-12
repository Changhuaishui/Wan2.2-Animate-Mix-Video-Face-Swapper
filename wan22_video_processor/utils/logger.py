"""
Logging utility for Wan2.2 Video Processor
"""
import logging
import sys
from pathlib import Path
from typing import Optional
from ..config.settings import Config


def setup_logger(
    name: str = "wan22_processor",
    level: Optional[str] = None,
    log_file: Optional[Path] = None,
    console: bool = True
) -> logging.Logger:
    """
    Set up and configure logger

    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
        console: Whether to output to console

    Returns:
        Configured logger instance
    """
    # Get or create logger
    logger = logging.getLogger(name)

    # Set level
    if level is None:
        level = Config.LOG_LEVEL
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(Config.LOG_FORMAT)

    # Add console handler if requested
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Add file handler if log file specified
    if log_file is None:
        log_file = Config.LOG_FILE

    try:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        # If file handler fails, log to console only
        if console:
            logger.warning(f"Failed to create file handler: {e}. Logging to console only.")

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


class LoggerMixin:
    """Mixin class to add logging capability to any class"""

    @property
    def logger(self) -> logging.Logger:
        """Get logger for the class"""
        if not hasattr(self, '_logger'):
            self._logger = setup_logger(self.__class__.__name__)
        return self._logger


if __name__ == "__main__":
    # Test logger
    logger = setup_logger("test_logger")
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
