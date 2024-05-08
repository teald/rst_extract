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
    _option_re = re.compile(r'^\s*:(\w+):\s*(.*)$', re.MULTILINE)

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

        if not self._data:
            raise ExtractionError('Empty file encountered')

        return self._data

    def _extract_code_blocks(self, rst_string: str | None = None) -> list[list[str]]:
        """Extract code blocks from the reStructuredText string."""
        log.debug('Extracting code blocks from file', filename=self.filename)

        if rst_string is None:
            rst_string = self._data
            log.debug('Using data from preloaded file', filename=self.filename)

        if rst_string is None:
            raise ExtractionError('No data to extract code blocks from')

        lines = rst_string.splitlines()

        # Get the lines where the code blocks start
        start_lines = (
            i for i, line in enumerate(lines) if self._code_block_re.match(line)
        )

        # TODO: This is just brute force implementation, could be cleaner.
        blocks_iter = (
            self._get_next_code_block(lines[start_line:]) for start_line in start_lines
        )

        # Consuming all above generators here.
        blocks = [self._filter_rst_options(block) for block in blocks_iter]

        return blocks

    def _filter_rst_options(self, block: list[str]) -> list[str]:
        """Filter out the reStructuredText options from the code block."""
        return [line for line in block if not self._option_re.match(line)]

    def _get_next_code_block(self, lines: list[str]) -> list[str]:
        """Get the next code block from the lines. This just gets the next
        dedent and returns those strings as a list.

        Arguments
        ---------
        lines
            The lines to extract the code block from.

        Returns
        -------
        list[str]
            The extracted code block.

        Raises
        ------
        ExtractionError
            If the code block does not start with the correct syntax. This
            should not happen if the code block is extracted from the
            reStructuredText file correctly. It should *include* the start of
            the block, which will be something along the lines of:
            ``.. code-block:: python``.
        """
        lines_iter = iter(lines)

        block_line = next(lines_iter)

        if not self._code_block_re.match(block_line):
            log.error(
                'Got string without code block start',
                line=block_line,
                lines=lines,
            )
            raise ExtractionError('Got string without code block start.')

        min_indent = None

        for i, line in enumerate(lines_iter):
            if min_indent is None:
                min_indent = len(line) - len(line.lstrip())

            if len(line) - len(line.lstrip()) < min_indent:
                return self._dedent_code_block(lines[:i])

        # The whole block is indented the same amount, assume the entire thing
        # is a code block.
        return self._dedent_code_block(lines[1:])

    @staticmethod
    def _dedent_code_block(block: list[str]) -> list[str]:
        """Dedent the code block. Does not modify the original list."""
        # Get the minimum indent
        # TODO: Could reimplement dedent with re.
        min_indent = min(
            len(line) - len(line.lstrip()) for line in block if line.strip()
        )

        return [line[min_indent:] for line in block]

    @staticmethod
    def _strip_empty_lines(block: list[str]) -> list[str]:
        """Strip empty lines from the code block."""
        return [line for line in block if line.strip()]

    @staticmethod
    def _convert_to_list_with_block_numbers(blocks: list[list[str]]) -> list[str]:
        """Convert the block to a list of tuples with line numbers."""
        all_lines = []

        # TODO: The start block label should be configurable.
        for i, block in enumerate(blocks, start=1):
            all_lines.append(f'# Block {i}:')
            all_lines.extend(block)

        return all_lines

    def _process_file(self) -> None:
        """Process the file to extract data."""
        log.debug('Processing file', filename=self.filename)

        blocks = self._extract_code_blocks()

        log.debug('Code blocks extracted', filename=self.filename)

        lines = self._convert_to_list_with_block_numbers(blocks)

        self._extracted_code = '\n'.join(lines)

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

        self._process_file()

        return self._extracted_code
