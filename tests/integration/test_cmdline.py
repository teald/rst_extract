"""Tests for the command line interface for rst_extract."""

import subprocess
import sys


def test_cmdline_help(capfd):
    """Test that the command line help message works."""
    subprocess.run([sys.executable, "-m", "rst_extract", "--help"], check=True)

    out, err = capfd.readouterr()
    assert "Extracts reStructuredText from Python files".lower() in out.lower()
    assert not err


def test_empty_file(empty_rst, capfd):
    """Test that an empty file does not raise an error."""
    subprocess.run([sys.executable, "-m", "rst_extract", str(empty_rst)], check=True)

    out, err = capfd.readouterr()
    assert not out
    assert not err


def test_code_file(code_only_rst, capfd):
    """Test that a file with only code does not raise an error."""
    subprocess.run(
        [sys.executable, "-m", "rst_extract", str(code_only_rst)], check=True
    )

    out, err = capfd.readouterr()
    assert not out
    assert not err
