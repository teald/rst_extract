"""Pytest testing configuration."""
# Ignore type hinting in mypy
# mypy: ignore-errors

import os
import shutil
from os.path import join

import pytest


# TODO: Helpers should probably not be in conftest.py.
class Helpers:
    _instance = None

    def __new__(cls) -> 'Helpers':
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):
        pass

    @staticmethod
    def dedent_code_block(block: list[str]) -> list[str]:
        """Dedent the code block. Does not modify the original list."""
        # Get the minimum indent
        min_indent = min(
            len(line) - len(line.lstrip()) for line in block if line.strip()
        )

        return [line[min_indent:] for line in block]

    @staticmethod
    def extract_end_code_rst(file_path: str) -> str:
        """Extract the end code from the rst file."""
        with open(file_path, 'r') as f:
            lines = f.readlines()

        end_line = [line.strip() == R'#~END~#' for line in lines]

        if sum(1 for result in end_line if result) > 1:
            raise ValueError('Multiple end lines found.')

        end_lines = lines[end_line.index(True) + 1 :]
        end_lines = [line.rstrip() for line in end_lines]

        # Dedent the code block to the minimum indent
        end_lines = Helpers.dedent_code_block(end_lines)

        # Remove whitespace on either side
        for i, line in enumerate(end_lines):
            if not line.strip():
                end_lines[i] = ''

        while end_lines[0] == '':
            end_lines.pop(0)

        # All but last bit of whitespace
        while all(not line.strip() for line in end_lines[-2:]):
            end_lines.pop(-1)

        return '\n'.join(end_lines)


@pytest.fixture
def test_file_dir() -> str:
    """Return the directory of the test files."""
    return join(os.path.dirname(__file__), 'tests/files')


@pytest.fixture
def empty_rst(tmp_path) -> str:
    """Create an empty rst file."""
    rst_file = join(tmp_path, 'empty.rst')

    with open(rst_file, 'w') as f:
        f.write('')

    return rst_file


@pytest.fixture
def code_only_rst(tmp_path, test_file_dir) -> str:
    """Create an rst file with only code."""
    # This file does not contain an END line to extract for completeness.
    file_name = R'only_code.rst'
    source_path = join(test_file_dir, file_name)

    temporary_file_path = join(tmp_path, file_name)

    shutil.copy(source_path, temporary_file_path)

    return temporary_file_path


@pytest.fixture
def code_only_rst_result(test_file_dir) -> str:
    """Expected output of code_only_rst."""
    # This file does not contain an END line to extract for completeness.
    with open(join(test_file_dir, 'only_code.rst'), 'r') as f:
        lines = f.readlines()

    # Remove first line (code block)
    lines.pop(0)

    # Remove whitespace on either side
    for i, line in enumerate(lines):
        if not line.strip():
            lines[i] = ''

    while lines[0] == '':
        lines.pop(0)

    while lines[-1] == '':
        lines.pop(-1)

    # Dedent the code block to the minimum indent
    min_indent = min(len(line) - len(line.lstrip()) for line in lines if line)

    # TODO: Declutter this fixture.
    lines = [line[min_indent:] for line in lines]
    lines = ['# Block 1:'] + lines + ['']
    lines = [line.rstrip() for line in lines]

    return '\n'.join(lines)


@pytest.fixture
def complex_code_block_rst(tmp_path, test_file_dir) -> str:
    """Create an rst file with a complex code block."""
    file_name = R'file_with_text_and_code.rst'
    source_path = join(test_file_dir, file_name)

    temporary_file_path = join(tmp_path, file_name)

    shutil.copy(source_path, temporary_file_path)

    return temporary_file_path


@pytest.fixture
def complex_code_block_rst_result(test_file_dir, helper_methods) -> str:
    """Get expected output from #~END~# in file_with_text_and_code.rst."""
    answer = helper_methods.extract_end_code_rst(
        join(test_file_dir, 'file_with_text_and_code.rst')
    )

    return answer


@pytest.fixture
def helper_methods() -> Helpers:
    """Extract the answer from the rst doc."""
    return Helpers()


# TODO: Extract these sample file fixtures into a more
#       general fixture that can be easily reused.
@pytest.fixture
def different_languages_rst(tmp_path, test_file_dir) -> os.PathLike[str]:
    file_name = R'non_python_code.rst'
    source_path = join(test_file_dir, file_name)

    temporary_file_path = join(tmp_path, file_name)

    shutil.copy(source_path, temporary_file_path)

    return temporary_file_path


@pytest.fixture
def different_languages_rst_result(test_file_dir, helper_methods) -> str:
    answer = helper_methods.extract_end_code_rst(
        join(test_file_dir, R'non_python_code.rst')
    )

    return answer


@pytest.fixture
def hello_extract_rst(tmp_path) -> os.PathLike[str]:
    filename = R'hello.rst'
    temporary_file_path = join(tmp_path, filename)

    rst_string = (
        'Hello, World!\n'
        '\n'
        '.. code-block:: python\n'
        '\n'
        '    print("Hello, World!")\n'
        '\n'
        '..\n'
        '   #~END~#\n'
        '\n'
        '   print("Hello, World!")\n'
    )

    with open(temporary_file_path, 'w') as f:
        f.write(rst_string)

    return temporary_file_path


@pytest.fixture
def hello_extract_rst_stdout() -> str:
    return 'Hello, World!\n'
