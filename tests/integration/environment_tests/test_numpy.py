"""Test rst-extract in a virtual environment with numpy.

These tests run in a virtual environment initialized with the following
packages:

+ Core packages installed with `python -m venv`
+ numpy

Since these tests are meant to be fully isolated from the development
environment, virtual environments will
"""

import subprocess
from pathlib import Path

import pytest


@pytest.fixture()
def example_string() -> str:
    code_lines = [
        'import numpy',
        '',
        'array = numpy.array([1, 2, 3], dtype=numpy.int8)',
        'print(f\'Array contains {", ".join(str(x) for x in array)}\')',
    ]

    # indenting the python code
    code_lines = ['    ' + line for line in code_lines]

    # Code-block line
    full_rst_string = ['.. code-block:: python'] + code_lines

    return '\n'.join(full_rst_string)


@pytest.fixture()
def example_string_expected_output() -> str:
    return 'Array contains 1, 2, 3'


@pytest.fixture()
def create_tmp_venv(tmp_path: Path) -> Path:
    venv_path = tmp_path / 'venv'
    venv_path.mkdir()

    # TODO: Probably better to handle the
    # Create a virtual environment in the tmp_path
    _ = subprocess.run(['python', '-m', 'venv', str(venv_path)], check=False)

    # Upgrade pip... there's surely a better way to do this.
    _ = subprocess.run(
        [str(venv_path / 'bin' / 'pip'), 'install', '--upgrade', 'pip'],
        check=False,
    )

    # Install numpy in the virtual environment
    _ = subprocess.run(
        [str(venv_path / 'bin' / 'pip'), 'install', 'numpy'],
        check=False,
    )

    return venv_path


@pytest.fixture()
def python_bin_path(create_tmp_venv: Path) -> Path:
    return create_tmp_venv / 'bin' / 'python'


def test_numpy_code_in_isolated_venv(
    example_string: str,
    example_string_expected_output: str,
    create_tmp_venv: Path,
    python_bin_path: Path,
    capfd: pytest.CaptureFixture[str],
) -> None:
    # Write the example code to a file
    code_file = create_tmp_venv / 'example.rst'
    with code_file.open('w') as f:
        _ = f.write(example_string)

    # Run the rst-extract command
    result = subprocess.run(
        [
            'python',  # This is the python executable
            '-m',
            'rst_extract',
            str(code_file),
            '--execute',
            '--python-bin',
            str(python_bin_path),
        ],
    )

    # Check that the command ran successfully
    assert result.returncode == 0

    captured = capfd.readouterr()
    assert example_string_expected_output in captured.out
    assert not captured.err
