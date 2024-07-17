import logging
import os
import sys

import structlog
from structlog.stdlib import LoggerFactory

LOGGING_ENV_VAR = 'RST_EXTRACT_LOGGING'


# TODO: Logging should eventually live in a separate file.
def configure_logging(verbose: int) -> None:
    """Configure logging for rst_extract."""
    if not verbose:
        level = logging.WARNING

    elif verbose == 1:
        level = logging.INFO

    elif verbose == 2:
        level = logging.DEBUG

    # Override the default logging configuration if environment variable is set.
    if env_var_value := os.getenv(LOGGING_ENV_VAR):
        env_var_value = env_var_value.lower()
        if env_var_value in {'debug', '3'}:
            level = logging.DEBUG

        elif env_var_value in {'info', '2'}:
            level = logging.INFO

        elif env_var_value in {'warning', '1'}:
            level = logging.WARNING

        elif env_var_value in {'error', '0'}:
            level = logging.ERROR

        else:
            logging.warning(
                'Invalid value for environment variable %s: %s. '
                'Defaulting to WARNING.',
                LOGGING_ENV_VAR,
                env_var_value,
            )

    logging.basicConfig(
        format='%(message)s',
        stream=sys.stdout,
        level=level,
    )

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt='iso'),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.ExceptionPrettyPrinter(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.BoundLogger,
        cache_logger_on_first_use=True,
    )
