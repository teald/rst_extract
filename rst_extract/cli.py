"""Command line interface for rst_extract.

To-do
-----
- Script execution (rstextract [options] [file])
- Help text (--help)
"""

import os

import click

from .extractor import Extractor

MAGNIFYING_GLASS = '\U0001f50d'
EXCLAMATION_MARK = '\U00002757'


@click.command()
@click.argument(
    'filename',
    nargs=-1,
    type=click.Path(exists=True),
)
def start(filename: list[os.PathLike[str]]) -> None:
    """Extract reStructuredText from Python files."""
    # TODO: Should eventually escape into an interactive selector.
    if not filename:
        click.echo(
            f'{EXCLAMATION_MARK} No filename provided. Please '
            f'provide a filename (or multiple).'
        )
        return

    click.echo(f'{MAGNIFYING_GLASS} Extracting reStructuredText from {filename}.')

    # TODO: This should be managed by a class, not in start().
    for file in filename:
        click.echo(f'{MAGNIFYING_GLASS} Processing {file}...')

        extractor = Extractor(file)
        rst = extractor.extract()

        click.echo(rst)
