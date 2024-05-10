"""Entry point for the rst_extract package.

It should be run as a module with the -m flag:
    python -m rst_extract

The CLI is also accessible as a script:
    rst-extract

Assuming installation has worked properly.
"""

from . import cli

cli.start()
