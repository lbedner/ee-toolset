import logging

import structlog
from icecream import ic
from icecream import install as install_ic

from app.core.config import settings

"""
This is the de-facto get_logger function to use throughout the application.
In other words, use this instead of `logging.getLogger()`.
"""
get_logger = structlog.stdlib.get_logger

JSON_FORMATTER = structlog.stdlib.ProcessorFormatter(
    processors=[
        # Add the name of the logger to event dict.
        structlog.stdlib.add_logger_name,
        # Add log level to event dict.
        structlog.stdlib.add_log_level,
        # Add a timestamp in ISO 8601 format.
        structlog.processors.TimeStamper(fmt="iso"),
        # Remove _record and _from_structlog from event_dict.
        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
        # Render the final event dict as JSON.
        structlog.processors.JSONRenderer(),
    ],
)

# https://www.structlog.org/en/stable/development.html
DEV_FORMATTER = structlog.stdlib.ProcessorFormatter(
    processors=[
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M.%S"),
        structlog.processors.StackInfoRenderer(),
        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
        structlog.dev.ConsoleRenderer(colors=True),
    ],
)

logger: structlog.stdlib.BoundLogger = structlog.get_logger()

# Install icecream globally so you don't have to import it everywhere
ic.configureOutput(includeContext=True)
install_ic()


def setup_logging() -> None:
    """
    Called during startup for any process that emits logs.
    """
    structlog.configure(
        processors=[
            # Prepare event dict for `ProcessorFormatter`.
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
        wrapper_class=structlog.stdlib.BoundLogger,
    )

    formatter = JSON_FORMATTER if settings.APP_ENV != "dev" else DEV_FORMATTER

    # Adjust log levels for external packages
    logging.getLogger("flet_core").setLevel(logging.INFO)

    # Use OUR `ProcessorFormatter` to format all `logging` entries.
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
