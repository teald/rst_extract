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

import os
import subprocess
import sys
import typing
from os import PathLike

import click

from .extractor import Extractor
from .logs import configure_logging

MAGNIFYING_GLASS = '\U0001f50d'
EXCLAMATION_MARK = '\U00002757'
RUNNER_EMOJI = '\U0001f3c3'

LOGGING_ENV_VAR = 'RST_EXTRACT_LOGGING'


def execute_command(python_bin: PathLike[str], code: str) -> None:
    """Execute the extracted code."""
    command = (python_bin, '-c', code)
    result = subprocess.run(command, capture_output=True)

    # Print the output of the command
    click.echo(f'{RUNNER_EMOJI} Output:', file=sys.stdout)
    click.echo(result.stdout.decode('utf-8'), file=sys.stdout)

    # Also print stderr if there is any
    if result.stderr:
        click.echo(f'{RUNNER_EMOJI} Error:', file=sys.stdout)
        click.echo(result.stderr.decode('utf-8'), file=sys.stdout)


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
@click.option(
    '--python-bin',
    nargs=1,
    type=click.Path(exists=True),
    default=sys.executable,
    help='Path to the Python binary to use for execution.',
)
def start(
    filename: list[os.PathLike[str]],
    output: typing.TextIO,
    verbose: int,
    execute: bool,
    python_bin: os.PathLike[str],
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

    click.echo(
        f'{MAGNIFYING_GLASS} Extracting reStructuredText from ',
        file=stdout_to,
    )
    click.echo(
        '\n'.join(f'{i:6d}) {file}' for i, file in enumerate(filename, start=1)),
        file=stdout_to,
    )

    # TODO: This should be managed by a class, not in start().
    results: dict[PathLike[str], str] = {}
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
            _ = output.write(result)

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
            execute_command(python_bin=python_bin, code=result)

    click.echo(f'{MAGNIFYING_GLASS} Done.'.ljust(80, '-'), file=stdout_to)
