"""Structured logging configuration for the application."""

import json
import logging
import sys
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging.

    Formats log records as JSON for easy parsing and analysis.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.

        Args:
            record: Log record to format

        Returns:
            JSON-formatted log string
        """
        log_data: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if hasattr(record, "extra"):
            log_data.update(record.extra)

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "stack_info") and record.stack_info:
            log_data["stack_info"] = self.formatStack(record.stack_info)

        return json.dumps(log_data)


class StandardFormatter(logging.Formatter):
    """Standard formatter for human-readable logging.

    Formats log records with timestamp, level, logger name, and message.
    """

    def __init__(self) -> None:
        """Initialize standard formatter."""
        fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        super().__init__(fmt=fmt, datefmt="%Y-%m-%d %H:%M:%S")


def setup_logging(debug: bool = False) -> None:
    """Configure application logging.

    Args:
        debug: Enable debug mode with more verbose logging
    """
    log_level = logging.DEBUG if debug else logging.INFO

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    if debug:
        formatter = StandardFormatter()
    else:
        formatter = JSONFormatter()

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)

    root_logger.info(
        "Logging configured",
        extra={
            "log_level": logging.getLevelName(log_level),
            "debug_mode": debug,
        },
    )
