"""Primary extraction class for extracting data from reStructuredText files."""

import os
import re

import structlog

# Log initialization
log = structlog.get_logger()


# Type hinting
_FILE_TYPE = str | os.PathLike[str]


class ExtractionError(Exception):
    """Exception raised when an error occurs during extraction."""

    pass


class Extractor:
    """Extract data from reStructuredText files."""

    _filename: _FILE_TYPE
    _data: str | None

    _code_block_re = re.compile(r'^.. code-block::\s*(\w+)?\s*$', re.MULTILINE)

    def __init__(self, filename: _FILE_TYPE):
        """Initialize Extractor object.

        Arguments
        ---------
        filename
            The filename of the reStructuredText file to extract data from.
        """
        self.filename = filename

        log.info('Extractor initialized', filename=self.filename)

    @property
    def full_code(self) -> str:
        """Get the full code extracted from the reStructuredText file."""
        return self._extract_code_blocks()

    @property
    def filename(self) -> _FILE_TYPE:
        """Get the filename of the Extractor."""
        return self._filename

    @filename.setter
    def filename(self, filename: _FILE_TYPE) -> None:
        """Set the filename of the Extractor."""
        self._filename = filename
        log.debug('Filename set', filename=self.filename)

        self._validate_filename()

        log.debug('Filename validated', filename=self.filename)

    def _validate_filename(self) -> None:
        """Validate the current filename of the Extractor."""
        # TODO: This should use some pydantic magic, probably, but this is the
        # alpha version.
        if not any(
            (
                isinstance(self.filename, str),
                isinstance(self.filename, os.PathLike),
            )
        ):
            raise TypeError(
                f'Expected filename to ahve type {_FILE_TYPE},'
                f' but got {type(self.filename)} instead.'
            )

    def _load_file_contents(self) -> str:
        """Load the contents of the reStructuredText file.

        Broadly, we are assuming this isn't a large (>> 1MB) file, so we can
        read the contents into memory in full.
        """
        # TODO: Encoding should probably be configurable, just in case.
        with open(self.filename, 'r', encoding='utf-8') as file:
            data = file.read()

        self._data = data

        log.debug('File contents loaded', filename=self.filename)

        return self._data

    def _extract_code_blocks(self, rst_string: str | None = None) -> str:
        """Extract code blocks from the reStructuredText string."""
        log.debug('Extracting code blocks from file', filename=self.filename)

        if rst_string is None:
            rst_string = self._data
            log.debug('Using data from preloaded file', filename=self.filename)

        if rst_string is None:
            raise ExtractionError('No data to extract code blocks from')

        lines = rst_string.splitlines()

        # Get the lines where the code blocks start
        start_lines = [
            i for i, line in enumerate(lines) if self._code_block_re.match(line)
        ]

        # TODO: This is just brute force implementation, could be cleaner.
        blocks = [
            self._get_next_code_block(lines[start_line:]) for start_line in start_lines
        ]

        blocks = [self._filter_rst_options(block) for block in blocks]

        raise NotImplementedError

        return 'barf'

    def _filter_rst_options(self, block: list[str]) -> list[str]:
        """Filter out the reStructuredText options from the code block."""
        raise NotImplementedError

    def _get_next_code_block(self, lines: list[str]) -> list[str]:
        """Get the next code block from the lines. This just gets the next
        dedent and returns those strings as a list.
        """
        lines_iter = iter(lines)
        next(lines_iter)  # Skip the code-block line

        min_indent = None

        for i, line in enumerate(lines_iter):
            if min_indent is None:
                min_indent = len(line) - len(line.lstrip())

            if len(line) - len(line.lstrip()) < min_indent:
                return lines[:i]

        raise ExtractionError('No dedent found for code block')

    def extract(self) -> str:
        """Extract data from the reStructuredText file.

        Returns
        -------
        str
            The extracted data from the reStructuredText file.
        """
        log.info('Extracting data from', filename=self.filename)

        try:
            self._load_file_contents()

        except FileNotFoundError as error:
            log.error('File not found', filename=self.filename)

            msg = str(error)

            raise ExtractionError(msg) from error

        return self.full_code
