"""Primary extraction class for extracting data from reStructuredText files."""

import os

import structlog

# Log initialization
log = structlog.get_logger()


# Type hinting
_FILE_TYPE = str | bytes | os.PathLike


class Extractor:
    """Extract data from reStructuredText files."""

    def __init__(self, filename: _FILE_TYPE):
        """Initialize Extractor object.

        Arguments:
        ---------
        filename : str | bytes | os.PathLike
            The filename of the reStructuredText file to extract data from.

        """
        self.filename = filename
