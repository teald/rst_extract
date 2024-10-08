"""Tests for the command line interface for rst_extract.

- TODO: Implement tests that use click's testing utilities.
"""

# Ignore type hinting in mypy
# mypy: ignore-errors
import glob
import subprocess
import sys
from pathlib import Path

import pytest


def test_cmdline_help(capfd: pytest.CaptureFixture[str]):
    """Test that the command line help message works."""
    _ = subprocess.run(
        [sys.executable, '-m', 'rst_extract', '--help'], check=True
    )

    out, err = capfd.readouterr()
    assert 'Extract reStructuredText from Python files'.lower() in out.lower()
    assert not err


def test_cmdline_no_args(capfd: pytest.CaptureFixture[str]):
    """Test that the command line interface works with no arguments."""
    _ = subprocess.run([sys.executable, '-m', 'rst_extract'], check=True)

    out, err = capfd.readouterr()
    assert 'no filename provided' in out.lower()
    assert not err


def test_empty_file(empty_rst: Path, capfd: pytest.CaptureFixture[str]):
    """Test that an empty file does not raise an error."""
    with pytest.raises(subprocess.CalledProcessError):
        _ = subprocess.run(
            [sys.executable, '-m', 'rst_extract', str(empty_rst)],
            check=True,
        )

    _, err = capfd.readouterr()
    assert 'empty file encountered' in err.lower()


def test_code_file(code_only_rst: Path, capfd: pytest.CaptureFixture[str]):
    """Test that a file with only code does not raise an error."""
    _ = subprocess.run(
        [sys.executable, '-m', 'rst_extract', str(code_only_rst)],
        check=True,
    )

    _, err = capfd.readouterr()
    assert not err


def test_complex_file(
    complex_code_block_rst: Path,
    complex_code_block_rst_result: str,
    capfd: pytest.CaptureFixture[str],
    tmp_path: Path,
):
    """Test that a complex file does not raise an error."""
    _ = subprocess.run(
        [sys.executable, '-m', 'rst_extract', str(complex_code_block_rst)],
        check=True,
    )

    out, err = capfd.readouterr()
    assert not err

    assert complex_code_block_rst_result in out


def test_different_langauges(
    different_languages_rst: Path,
    different_languages_rst_result: str,
    capfd: pytest.CaptureFixture[str],
    tmp_path: Path,
):
    """Test that a file with different languages does not raise an error."""
    _ = subprocess.run(
        [sys.executable, '-m', 'rst_extract', str(different_languages_rst)],
        check=True,
    )

    out, err = capfd.readouterr()
    assert not err

    assert different_languages_rst_result in out


def test_output_file(
    complex_code_block_rst: Path,
    complex_code_block_rst_result: str,
    capfd: pytest.CaptureFixture[str],
    tmp_path: Path,
):
    """Test that a complex file does not raise an error."""
    output_file = tmp_path / 'output.py'
    _ = subprocess.run(
        [
            sys.executable,
            '-m',
            'rst_extract',
            str(complex_code_block_rst),
            '-o',
            str(output_file),
        ],
        check=True,
    )

    out, err = capfd.readouterr()
    assert not err

    assert complex_code_block_rst_result in out

    with open(output_file) as f:
        assert complex_code_block_rst_result in f.read()


def test_execute_extraction(
    hello_extract_rst: Path,
    hello_extract_rst_stdout: str,
):
    """Test that the extraction code works."""
    result = subprocess.run(
        [
            sys.executable,
            '-m',
            'rst_extract',
            hello_extract_rst,
            '--execute',
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert hello_extract_rst_stdout.strip() == result.stdout.strip()
    assert not result.stderr
    assert result.returncode == 0


def test_execute_code_with_imported_decorators(
    code_with_imported_decorators_rst: Path,
    code_with_imported_decorators_rst_stdout: str,
):
    """Test that the extraction code works."""
    result = subprocess.run(
        [
            sys.executable,
            '-m',
            'rst_extract',
            code_with_imported_decorators_rst,
            '--execute',
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert (
        code_with_imported_decorators_rst_stdout.strip()
        == result.stdout.strip()
    )
    assert not result.stderr
    assert result.returncode == 0


def test_execute_code_with_imported_decorators_fail(
    code_with_imported_decorators_rst: Path,
):
    """Test that the extraction code works."""
    with pytest.raises(subprocess.CalledProcessError):
        _ = subprocess.run(
            [
                sys.executable,
                '-m',
                'rst_extract',
                code_with_imported_decorators_rst,
                '--execute',
                '--isolate-blocks',
            ],
            check=True,
            capture_output=True,
            text=True,
        )


# Run the command line tests over all test files -- just get them with glob for
# now.
_ALL_FILES: list[Path] = [Path(f) for f in glob.glob('tests/files/*.rst')]


@pytest.mark.parametrize('test_file', _ALL_FILES)
def run_cli_on_all_test_files(test_file: Path):
    """Run the command line tests on all test files."""
    result = subprocess.run(
        [
            sys.executable,
            '-m',
            'rst_extract',
            test_file,
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert not result.stderr
    assert result.returncode == 0
    assert result.stdout
