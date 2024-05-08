"""Pytest testing configuration."""
# Ignore type hinting in mypy
# mypy: ignore-errors

import os
import shutil
from os.path import join
from typing import Callable

import pytest


@pytest.fixture
def test_file_dir() -> str:
    """Return the directory of the test files."""
    return join(os.path.dirname(__file__), 'tests/files')


@pytest.fixture
def empty_rst(tmpdir) -> str:
    """Create an empty rst file."""
    rst_file = join(tmpdir, 'empty.rst')

    with open(rst_file, 'w') as f:
        f.write('')

    return rst_file


@pytest.fixture
def code_only_rst(tmpdir, test_file_dir) -> str:
    """Create an rst file with only code."""
    file_name = R'only_code.rst'
    source_path = join(test_file_dir, file_name)

    temporary_file_path = join(tmpdir, file_name)

    shutil.copy(source_path, temporary_file_path)

    return temporary_file_path


@pytest.fixture
def code_only_rst_result(test_file_dir) -> str:
    """Expected output of code_only_rst."""
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
    lines = ['# Block 1:'] + [''] + lines
    lines = [line.rstrip() for line in lines]

    return '\n'.join(lines)


@pytest.fixture
def complex_code_block_rst(tmpdir, test_file_dir) -> str:
    """Create an rst file with a complex code block."""
    file_name = R'file_with_text_and_code.rst'
    source_path = join(test_file_dir, file_name)

    temporary_file_path = join(tmpdir, file_name)

    shutil.copy(source_path, temporary_file_path)

    return temporary_file_path


@pytest.fixture
def complex_code_block_rst_result(test_file_dir) -> str:
    """Get expected output from #~END~# in file_with_text_and_code.rst."""
    answer = extract_answer_from_rst_doc(
        join(test_file_dir, 'file_with_text_and_code.rst')
    )

    breakpoint(0)

    return answer


def _dedent_code_block(block: list[str]) -> list[str]:
    """Dedent the code block. Does not modify the original list."""
    # Get the minimum indent
    min_indent = min(len(line) - len(line.lstrip()) for line in block if line.strip())

    return [line[min_indent:] for line in block]


def _extract_end_code_rst(file_path: str) -> str:
    """Extract the end code from the rst file."""
    with open(file_path, 'r') as f:
        lines = f.readlines()

    end_line = [line.strip() == R'#~END~#' for line in lines]

    if sum(1 for result in end_line if result) > 1:
        raise ValueError('Multiple end lines found.')

    end_lines = lines[end_line.index(True) + 1 :]

    # Dedent the code block to the minimum indent
    end_lines = _dedent_code_block(end_lines)

    return '\n'.join(end_lines)


@pytest.fixture(autouse=True)
def extract_answer_from_rst_doc() -> Callable:
    """Extract the answer from the rst doc."""
    return _extract_end_code_rst
