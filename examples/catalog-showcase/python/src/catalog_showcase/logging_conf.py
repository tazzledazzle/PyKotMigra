"""Structured logging setup (catalog: structured logging)."""

from __future__ import annotations

import logging.config


def configure_logging() -> None:
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "jsonish": {
                    "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
                },
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "formatter": "jsonish",
                },
            },
            "root": {"level": "INFO", "handlers": ["default"]},
            "loggers": {
                "catalog_showcase": {"level": "INFO", "propagate": True},
            },
        }
    )
