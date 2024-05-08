"""Pytest testing configuration."""
# Ignore type hinting in mypy
# mypy: ignore-errors

import os
import shutil
from os.path import join

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
