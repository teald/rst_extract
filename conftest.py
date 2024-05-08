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
        return f.read()

    raise NotImplementedError
