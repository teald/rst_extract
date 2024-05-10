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
import typing

import click
import structlog
from structlog.stdlib import LoggerFactory

from .extractor import Extractor

MAGNIFYING_GLASS = '\U0001f50d'
EXCLAMATION_MARK = '\U00002757'
RUNNER_EMOJI = '\U0001f3c3'


# TODO: Logging should eventually live in a separate file.
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


@click.command()
@click.argument(
    'filename',
    nargs=-1,
    type=click.Path(exists=True),
)
@click.option(
    '-o',
    '--output',
    type=click.File('w+'),
    nargs=1,
    show_default=True,
    help='Output to a file. The output will be python code.',
)
@click.option(
    '-v',
    '--verbose',
    default=0,
    type=int,
    count=True,
    help='Increase verbosity. Can be used multiple times. Maximum is DEBUG (-vvv).',
)
@click.option(
    '--execute',
    is_flag=True,
    help='Execute the extracted code.',
)
def start(
    filename: list[os.PathLike[str]],
    output: typing.TextIO,
    verbose: int,
    execute: bool,
) -> None:
    """Extract reStructuredText from Python files."""
    configure_logging(verbose)

    # TODO: Should be managed by an STDOUT manager class.
    stdout_to = sys.stdout
    if not verbose:
        stdout_to = open(os.devnull, 'w')

    # TODO: Should eventually escape into an interactive selector.
    if not filename:
        click.echo(
            f'{EXCLAMATION_MARK} No filename provided. Please '
            f'provide a filename (or multiple).',
        )
        return

    click.echo(f'{MAGNIFYING_GLASS} Extracting reStructuredText from ', file=stdout_to)
    click.echo(
        '\n'.join(f'{i:6d}) {file}' for i, file in enumerate(filename, start=1)),
        file=stdout_to,
    )

    # TODO: This should be managed by a class, not in start().
    results = {}
    for file in filename:
        click.echo(f'{MAGNIFYING_GLASS} Processing {file}...', file=stdout_to)

        extractor = Extractor(file)
        result = extractor.extract()

        results[file] = result

    # TODO: Output should be managed by a class, not in start().
    if output:
        for file, result in results.items():
            click.echo(
                f'{MAGNIFYING_GLASS} Writing {file} to {output.name}...',
                file=stdout_to,
            )
            output.write(result)

    # TODO: Execution should be managed by a class, not in start().
    if not execute:
        for file, result in results.items():
            # TODO: Make primary output prettier and parsable.
            msg = f'{MAGNIFYING_GLASS} {file}'.ljust(80, '-')
            click.echo(msg)
            click.echo(result)

    if execute:
        for file, result in results.items():
            click.echo(f'{RUNNER_EMOJI} Executing {file}...', file=stdout_to)
            exec(result)

    click.echo(f'{MAGNIFYING_GLASS} Done.'.ljust(80, '-'), file=stdout_to)
