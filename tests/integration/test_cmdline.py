"""Tests for the command line interface for rst_extract.

- TODO: Implement tests that use click's testing utilities.
"""
# Ignore type hinting in mypy
# mypy: ignore-errors

import subprocess
import sys

import pytest


def test_cmdline_help(capfd):
    """Test that the command line help message works."""
    subprocess.run([sys.executable, '-m', 'rst_extract', '--help'], check=True)

    out, err = capfd.readouterr()
    assert 'Extract reStructuredText from Python files'.lower() in out.lower()
    assert not err


def test_cmdline_no_args(capfd):
    """Test that the command line interface works with no arguments."""
    subprocess.run([sys.executable, '-m', 'rst_extract'], check=True)

    out, err = capfd.readouterr()
    assert 'no filename provided' in out.lower()
    assert not err


def test_empty_file(empty_rst, capfd):
    """Test that an empty file does not raise an error."""
    with pytest.raises(subprocess.CalledProcessError):
        subprocess.run(
            [sys.executable, '-m', 'rst_extract', str(empty_rst)], check=True
        )

    out, err = capfd.readouterr()
    assert 'empty file encountered' in err.lower()


def test_code_file(code_only_rst, capfd):
    """Test that a file with only code does not raise an error."""
    subprocess.run(
        [sys.executable, '-m', 'rst_extract', str(code_only_rst)], check=True
    )

    out, err = capfd.readouterr()
    assert not err


def test_complex_file(
    complex_code_block_rst,
    complex_code_block_rst_result,
    capfd,
    tmp_path,
):
    """Test that a complex file does not raise an error."""
    subprocess.run(
        [sys.executable, '-m', 'rst_extract', str(complex_code_block_rst)],
        check=True,
    )

    out, err = capfd.readouterr()
    assert not err

    assert complex_code_block_rst_result in out


def test_diffent_langauges(
    different_languages_rst,
    different_languages_rst_result,
    capfd,
    tmp_path,
):
    """Test that a file with different languages does not raise an error."""
    subprocess.run(
        [sys.executable, '-m', 'rst_extract', str(different_languages_rst)],
        check=True,
    )

    out, err = capfd.readouterr()
    assert not err

    assert different_languages_rst_result in out


def test_output_file(
    complex_code_block_rst,
    complex_code_block_rst_result,
    capfd,
    tmp_path,
):
    """Test that a complex file does not raise an error."""
    output_file = tmp_path / 'output.py'
    subprocess.run(
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

    with open(output_file, 'r') as f:
        assert complex_code_block_rst_result in f.read()
