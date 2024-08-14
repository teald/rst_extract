"""Primary extraction class for extracting data from reStructuredText files."""

import os
import re
import typing

import structlog

# Log initialization
log = structlog.get_logger()


# Type hinting
_FILE_TYPE = str | os.PathLike[str]


class ExtractionError(Exception):
    """Exception raised when an error occurs during extraction."""


class Extractor:
    """Extract data from reStructuredText files."""

    _filename: _FILE_TYPE
    _data: str | None

    _code_block_re = re.compile(r'^.. code-block::\s*python\s*$', re.MULTILINE)
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
            ),
        ):
            raise TypeError(
                f'Expected filename to ahve type {_FILE_TYPE},'
                f' but got {type(self.filename)} instead.',
            )

    def _load_file_contents(self) -> str:
        """Load the contents of the reStructuredText file.

        Broadly, we are assuming this isn't a large (>> 1MB) file, so we can
        read the contents into memory in full.
        """
        # TODO: Encoding should probably be configurable, just in case.
        with open(self.filename, encoding='utf-8') as file:
            data = file.read()

        self._data = data

        log.debug('File contents loaded', filename=self.filename)

        if not self._data:
            raise ExtractionError('Empty file encountered')

        return self._data

    def _extract_code_blocks(
        self, rst_string: str | None = None
    ) -> list[list[str]]:
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
            i
            for i, line in enumerate(lines)
            if self._code_block_re.match(line)
        ]

        # TODO: This is just brute force implementation, could be cleaner.
        blocks_iter = (
            self._get_next_code_block(lines[start_line:])
            for start_line in start_lines
        )

        # Consuming all above generators here.
        blocks = [self._filter_rst_options(block) for block in blocks_iter]
        log.debug('Code blocks extracted', filename=self.filename)

        return blocks

    def _filter_rst_options(self, block: list[str]) -> list[str]:
        """Filter out the reStructuredText options from the code block."""
        return [line for line in block if not self._option_re.match(line)]

    @staticmethod
    def _get_indent_space_count(line: str) -> int:
        """Get the number of spaces in the indent of the line."""
        return len(line) - len(line.lstrip())

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
            if min_indent is None and line.strip():
                min_indent = self._get_indent_space_count(line)

            # Occurs if there is no content at the top of the code block.
            if min_indent is None:
                continue

            if line and self._get_indent_space_count(line) < min_indent:
                return self._dedent_code_block(lines[1:i])

        # The whole block is indented the same amount, assume the entire thing
        # is a code block.
        return self._dedent_code_block(lines[1:])

    @staticmethod
    def _dedent_code_block(block: list[str]) -> list[str]:
        """Dedent the code block. Does not modify the original list."""
        # Get the minimum indent
        # TODO: Could reimplement dedent with re.
        get_indent_space_count = Extractor._get_indent_space_count
        min_indent = min(
            get_indent_space_count(line) for line in block if line.strip()
        )

        return [line[min_indent:] for line in block]

    @staticmethod
    def _strip_empty_lines(block: list[str]) -> list[str]:
        """Strip empty lines from the code block."""
        return [line for line in block if line.strip()]

    @staticmethod
    def _trim_empty_lines(block: list[str]) -> list[str]:
        """Trim empty lines from the end of the code block."""
        while block and not block[0].strip():
            block.pop(0)

        while block and not block[-1].strip():
            block.pop()

        return block

    @staticmethod
    def _convert_to_list_with_block_numbers(
        blocks: list[list[str]],
    ) -> list[str]:
        """Convert the block to a list of tuples with line numbers."""
        all_lines = []

        # TODO: The start block label should be configurable.
        for i, block in enumerate(blocks, start=1):
            all_lines.append(f'# Block {i}:')
            all_lines.extend(Extractor._trim_empty_lines(block))

            # The last line of the block should have a newline after it.
            all_lines.append('')

        while all_lines and all(not line.strip() for line in all_lines[-2:]):
            all_lines.pop()

        return all_lines

    def _process_file(self) -> None:
        """Process the data to extract data."""
        log.debug('Processing file', filename=self.filename)
        blocks = self._extract_code_blocks()
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

    def export_to_file(self, output: typing.TextIO) -> None:
        """Export the extracted data to a file.

        Arguments
        ---------
        output
            The file stream to output the extracted data to.
        """
        log.info('Exporting data to', output=output)

        output.write(self._extracted_code)

        log.info('Data exported', output=output)

    def execute(self) -> None:
        """Extract the python code and execute it like a standalone file."""
        log.info('Executing extracted code', filename=self.filename)

        exec(self._extracted_code)

        log.info('Code executed', filename=self.filename)
