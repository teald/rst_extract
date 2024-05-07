"""A Python package for extracting reStructuredText from Python files.

`rst_extract` provides a command line interface for extracting reStructuredText
from Python files. It is useful for extracting docstrings from Python files and
converting them to reStructuredText.
"""

from . import cli, extractor
from .extractor import Extractor

__all__ = [
    'cli',
    'extractor',
    'Extractor',
]
