"""Tests for the command line interface for rst_extract."""

import subprocess
import sys


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
    subprocess.run([sys.executable, '-m', 'rst_extract', str(empty_rst)], check=True)

    out, err = capfd.readouterr()
    assert 'empty file encountered' in out.lower()


def test_code_file(code_only_rst, capfd):
    """Test that a file with only code does not raise an error."""
    subprocess.run(
        [sys.executable, '-m', 'rst_extract', str(code_only_rst)], check=True
    )

    out, err = capfd.readouterr()
    assert not err
