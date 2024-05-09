"""Command line interface for rst_extract.

To-do
-----
- [ ] Implement an interactive selector for multiple files.
- [x] Implement a flag for verbosity.
    - [x] -v for INFO
    - [x] -vv for DEBUG
    - [x] default to WARNING
    - [ ] Make output handled with this, too, so there's not undesirable stdout
          output without being requested.
- [ ] Implement a debug mode.
- [ ] Implement a version flag.
- [ ] Implement a flag to output to a file.
    - [ ] Implement a flag to run the output directly.
- [ ] Implement a flag to output log messages to a file.
"""

import logging
import os
import sys

import click
import structlog
from structlog.stdlib import LoggerFactory

from .extractor import Extractor

_VERBOSE_OPTION = click.option(
    '-v',
    '--verbose',
    default=0,
    type=int,
    count=True,
    help='Increase verbosity. Can be used multiple times. Maximum is DEBUG (-vvv).',
)


# TODO: Logging should eventually live in a separate file.
@click.command()
@_VERBOSE_OPTION
def configure_logging(verbose: int) -> None:
    """Configure logging for rst_extract."""
    if not verbose:
        level = logging.WARNING

    elif verbose == 1:
        level = logging.INFO

    elif verbose == 2:
        level = logging.DEBUG

    logging.basicConfig(
        format='%(message)s',
        stream=sys.stdout,
        level=level,
    )

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt='iso'),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.ExceptionPrettyPrinter(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.BoundLogger,
        cache_logger_on_first_use=True,
    )


MAGNIFYING_GLASS = '\U0001f50d'
EXCLAMATION_MARK = '\U00002757'


@click.command()
@click.argument(
    'filename',
    nargs=-1,
    type=click.Path(exists=True),
)
@click.option(
    '-o',
    '--output',
    default='./rst_extract.output.py',
    type=click.Path(),
    help='Output to a file. The output will be python code.',
)
def start(
    filename: list[os.PathLike[str]],
    output: os.PathLike[str],
) -> None:
    """Extract reStructuredText from Python files."""
    # TODO: Should eventually escape into an interactive selector.
    if not filename:
        click.echo(
            f'{EXCLAMATION_MARK} No filename provided. Please '
            f'provide a filename (or multiple).'
        )
        return

    click.echo(f'{MAGNIFYING_GLASS} Extracting reStructuredText from ')
    click.echo('\n'.join(f'{i:6d}) {file}' for i, file in enumerate(filename, start=1)))

    # TODO: This should be managed by a class, not in start().
    results = {}
    for file in filename:
        click.echo(f'{MAGNIFYING_GLASS} Processing {file}...')

        extractor = Extractor(file)
        result = extractor.extract()

        results[file] = result

    for file, result in results.items():
        # TODO: Make primary output prettier and parsable.
        msg = f'{MAGNIFYING_GLASS} {file}'.ljust(80, '-')
        click.echo(msg)
        click.echo(result)

    extractor.export_to_file(output)

    click.echo(f'{MAGNIFYING_GLASS} Done.'.ljust(80, '-'))
