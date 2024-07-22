"""Code block with metadata about the original RST file."""

import re
from typing import ClassVar, Optional, Sequence

from pydantic import BaseModel, FilePath, StrictInt, StrictStr, field_validator


class BlockError(ValueError):
    """Error raised when a block is not properly formatted."""


class Block(BaseModel):
    code: list[StrictStr] = []
    offsets: dict[StrictInt, StrictInt] = {}
    path: Optional[FilePath | str] = None

    # RST-specific metadata
    directive: Optional[StrictStr] = None
    options: Sequence[StrictStr] = tuple()

    # Regex patterns
    _directive_pattern: ClassVar[str] = r'\.\. ([\w\-]+)::'
    _options_pattern: ClassVar[str] = r'\s+:(\w+):'
    _indent_pattern: ClassVar[str] = r'^(\s+)'

    @field_validator('path')
    @classmethod
    def _convert_path(cls, value: FilePath | str) -> FilePath:
        """Convert a string to a FilePath object."""
        if isinstance(value, str):
            return FilePath(value)

        return value

    @field_validator('options')
    @classmethod
    def _convert_options(cls, value: Sequence[StrictStr]) -> tuple[StrictStr, ...]:
        """Convert the sequence to a tuple, for consistency/immutability."""
        return tuple(v for v in value)

    @staticmethod
    def from_string(string: StrictStr) -> 'Block':
        """This method expects that the string is only a code block.
        That means there is no excess text before or after the code block.

        If that is not the case, the method will raise an error.

        Raises
        ------
        BlockError
            If the string does not contain a code block, or if there is
            extraneous text around the code block.
        """
        directive = Block._get_directive(string)
        options = Block._get_options(string)
        code = Block._get_code(string)
        offset = Block._get_offset(string)

        new_block = Block(
            code=code,
            offsets=offset,
            directive=directive,
            options=options,
        )

        return new_block

    @staticmethod
    def _get_directive(string: StrictStr) -> Optional[StrictStr]:
        """Retrieve the directive and its line number from the string."""
        match = re.search(Block._directive_pattern, string)

        if not match:
            return None

        # Get the line number of the directive
        directive = match.group(1)

        return directive

    @staticmethod
    def _get_options(string: StrictStr) -> tuple[StrictStr, ...]:
        match = re.search(Block._options_pattern, string)

        if not match:
            return tuple()

        return tuple(match.group(1).split())

    @staticmethod
    def _get_code(string: StrictStr) -> list[StrictStr]:
        for line in string.split('\n'):
            if indent := re.match(Block._indent_pattern, line):
                break

        if not indent:
            raise BlockError('No code block found.')

        indent_str = indent.group(1)
        code = string.split('\n')

        # Remove the directive and options
        code = [
            line
            for line in code
            if not re.match(Block._directive_pattern, line)
            and not re.match(Block._options_pattern, line)
        ]

        # Remove the indent_str from each line
        code = [line.replace(indent_str, '', 1) for line in code]

        # Remove whitespace from the beginning and end of the code block
        code = Block._trim_list(code)

        return code

    @staticmethod
    def _trim_list(lines: list[StrictStr]) -> list[StrictStr]:
        """Remove whitespace from the beginning and end of a list of strings."""
        while lines[0] == '':
            lines.pop(0)

        while lines[-1] == '':
            lines.pop(-1)

        return lines

    @staticmethod
    def _get_offset(
        string: StrictStr,
        line_number: StrictInt = 0,
    ) -> dict[StrictInt, StrictInt]:
        """Get offset of the code block from the directive.

        This assumes the string can be split using the newline character.

        Arguments
        ---------
        string : str
            The string containing the code block.

        line_number : int
            The line number of the directive.

        Returns
        -------
        dict[int, int]
            A dictionary with the line number of the directive as the key
            and the line number of the first line of code as the value.
        """
        lines = string.split('\n')

        for i, line in enumerate(lines, start=line_number):
            if (
                not re.match(Block._options_pattern, line)
                and not re.match(Block._directive_pattern, line)
                and line.strip()
            ):
                break

        first_code_line = i

        return {0: first_code_line}
