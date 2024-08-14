"""A Python package for extracting reStructuredText from Python files.

`rst_extract` provides a command line interface for extracting reStructuredText
from Python files. It is useful for extracting docstrings from Python files and
converting them to reStructuredText.
"""

# Initialize logging if no other logging system is instantiated.
import logging

from . import cli, extractor
from .api import extract
from .extractor import Extractor
from .logs import configure_logging
from .validator import Validator

if not logging.getLogger().handlers:
    # Use structlog for logging.
    configure_logging(verbose=0)


__all__ = [
    'cli',
    'extract',
    'extractor',
    'Extractor',
    'Validator',
]
