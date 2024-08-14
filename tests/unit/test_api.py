"""Test the API for rst-extract."""

from pathlib import Path

import pytest

from rst_extract.api import extract
from rst_extract.extractor import ExtractionError


def test_extract_no_args() -> None:
    with pytest.raises(TypeError):
        extract()


def test_extract_empty_file(
    empty_rst: Path, capfd: pytest.CaptureFixture[str]
):
    """Test that an empty file does not raise an error."""
    with pytest.raises(ExtractionError):
        extract(empty_rst)


def test_extract_code_file(
    code_only_rst: Path, capfd: pytest.CaptureFixture[str]
):
    """Test that a file with only code does not raise an error."""
    _ = extract(code_only_rst)

    _, err = capfd.readouterr()
    assert not err


def test_complex_file(
    complex_code_block_rst: Path,
    complex_code_block_rst_result: str,
    capfd: pytest.CaptureFixture[str],
    tmp_path: Path,
):
    """Test that a complex file does not raise an error."""
    result = extract(complex_code_block_rst)

    out, err = capfd.readouterr()
    assert not err

    assert complex_code_block_rst_result in result


def test_different_languages(
    different_languages_rst: Path,
    different_languages_rst_result: str,
    capfd: pytest.CaptureFixture[str],
    tmp_path: Path,
):
    """Test that a file with different languages does not raise an error."""
    result = extract(different_languages_rst)

    out, err = capfd.readouterr()
    assert not err

    assert different_languages_rst_result in result


def test_output_file(
    complex_code_block_rst: Path,
    complex_code_block_rst_result: str,
    capfd: pytest.CaptureFixture[str],
    tmp_path: Path,
):
    """Test that an output file is written."""
    output = tmp_path / 'output.rst'
    result = extract(complex_code_block_rst, output)

    assert output.exists()
    with open(output, 'r') as f:
        assert complex_code_block_rst_result in f.read()

    assert complex_code_block_rst_result in result


def test_execute_code(
    hello_extract_rst: Path,
    hello_extract_rst_stdout: str,
    capfd: pytest.CaptureFixture[str],
):
    """Test that code is executed."""
    _ = extract(hello_extract_rst, execute=True)

    out, err = capfd.readouterr()
    assert not err

    assert 'Hello, World!' in out


def test_execute_code_with_imported_decorators(
    code_with_imported_decorators_rst: Path,
    code_with_imported_decorators_rst_stdout: str,
    capfd: pytest.CaptureFixture[str],
):
    """Test that code is executed with imported decorators."""
    _ = extract(code_with_imported_decorators_rst, execute=True)

    out, err = capfd.readouterr()
    assert not err

    assert code_with_imported_decorators_rst_stdout.strip() == out.strip()
