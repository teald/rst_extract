"""API for rst-extract. This is currently a very copy of what the CLI does."""

import os
import sys
from pathlib import Path

# TODO(teald): Bring this out of the CLI.
from .cli import execute_command
from .extractor import Extractor
from .logs import configure_logging


def extract(
    filename: os.PathLike[str],
    output: str | Path | None = None,
    python_bin: str | Path | None = None,
    *,
    execute: bool = False,
    verbose: int = 0,
) -> str:
    """Extract reStructuredText from Python files.

    Arguments
    ---------
    filename : os.PathLike[str]
        The filename to extract reStructuredText from.

    output : str | Path | None
        The output file to write the extracted reStructuredText to.

    python_bin : str | Path | None
        The Python binary to use for execution.

    execute : bool
        Whether to execute the extracted code after extraction.

    verbose : int
        The verbosity level. 0 is the default, 1 is INFO, 2 is DEBUG. Default
        is 0.

    Returns
    -------
    str
        The extracted python in the reStructuredText file.

    Warning
    -------
    This function executes code. Be careful what you pass to it, there are no
    safety guarantees.
    """
    configure_logging(verbose)
    extractor = Extractor(filename)
    result = extractor.extract()

    if output:
        with open(output, 'w') as f:
            f.write(result)

    if execute and Path(filename).exists():
        if python_bin is None:
            python_bin = sys.executable

        execute_command(python_bin=python_bin, code=result)

    return result
