"""Logging helpers for the Iron Dillo Cybersecurity Buddy."""

from __future__ import annotations

import logging
from logging.config import dictConfig
from typing import Any, Dict

from .config import Settings, get_settings

__all__ = ["configure_logging", "get_logger"]


def _build_logging_config(level: str) -> Dict[str, Any]:
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "structured": {
                "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": level,
                "formatter": "structured",
            }
        },
        "loggers": {
            "iron_dillo": {
                "handlers": ["console"],
                "level": level,
                "propagate": False,
            }
        },
        "root": {
            "handlers": ["console"],
            "level": level,
        },
    }


def configure_logging(settings: Settings | None = None) -> logging.Logger:
    """Configure and return the package logger."""

    settings = settings or get_settings()
    dictConfig(_build_logging_config(settings.log_level))
    logger = logging.getLogger("iron_dillo")
    logger.debug("Logging configured", extra={"environment": settings.environment})
    return logger


def get_logger(name: str) -> logging.Logger:
    """Return a child logger derived from the package root logger."""

    configure_logging()
    return logging.getLogger(f"iron_dillo.{name}")
