"""Command line interface for rst_extract.

To-do
-----
- Script execution (rstextract [options] [file])
- Help text (--help)
"""

import click

MAGNIFYING_GLASS = "\U0001f50d"


@click.command()
@click.argument(
    "filename",
    nargs=-1,
    type=click.Path(exists=True),
)
def start(filename):
    """Extract reStructuredText from Python files."""
    # TODO: Should eventually escape into an interactive selector.
    if not filename:
        click.echo(
            f"{MAGNIFYING_GLASS} No filename provided. Please "
            f"provide a filename (or multiple)."
        )
        return

    click.echo(f"{MAGNIFYING_GLASS} Extracting reStructuredText from {filename}.")
