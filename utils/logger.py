"""
Centralized logging configuration using loguru
"""
import sys
from pathlib import Path
from loguru import logger

from config import Config


def setup_logger(
    log_level: str = None,
    log_file: str = None,
    rotation: str = None,
    retention: str = None,
    format_string: str = None
):
    """
    Configure loguru logger with console and file output

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Path to log file (default: logs/townhall_{time}.log)
        rotation: When to rotate log files (default: "1 day")
        retention: How long to keep old logs (default: "30 days")
        format_string: Custom log format
    """
    # Remove default logger
    logger.remove()

    # Use config defaults if not provided
    log_level = log_level or Config.LOG_LEVEL
    rotation = rotation or Config.LOG_ROTATION
    retention = retention or Config.LOG_RETENTION
    format_string = format_string or Config.LOG_FORMAT

    # Add console handler with colors
    logger.add(
        sys.stderr,
        format=format_string,
        level=log_level,
        colorize=True,
        backtrace=True,
        diagnose=True
    )

    # Add file handler
    if log_file is None:
        Config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        log_file = Config.LOGS_DIR / "townhall_{time:YYYY-MM-DD}.log"

    logger.add(
        str(log_file),
        format=format_string,
        level=log_level,
        rotation=rotation,
        retention=retention,
        compression="zip",
        backtrace=True,
        diagnose=True
    )

    logger.info(f"Logger initialized - Level: {log_level}, Output: console + {log_file}")

    return logger


def get_logger():
    """Get the configured logger instance"""
    return logger
