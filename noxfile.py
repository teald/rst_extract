# Ignore mypy for this file, for now
# mypy: ignore-errors
# TODO(teald): Add type hints to this file.
# TODO(teald): Add build + build testing to noxfile.property
# TODO(teald): Add publishing steps to noxfile
from __future__ import annotations

import functools
import os
from pathlib import Path
from typing import Callable

import nox


class TestSettings:
    # Python versions to test against.
    python: list[str] = ['3.10', '3.11', '3.12']

    # Nox sessions to run by default.
    sessions: list[str] = [
        'unit_tests',
        'integration_tests',
        'coverage_report',
    ]

    _LOGGING_LEVEL = os.getenv('RST_EXTRACT_LOGGING')

    @classmethod
    def log_level(cls) -> str:
        """Get the logging level for the tests. Defaults to 'INFO'."""
        return cls._LOGGING_LEVEL or 'WARNING'


# These settings are used for local development.
# TODO: Override these in CI.
nox.options.sessions = TestSettings.sessions
nox.options.reuse_existing_virtualenvs = True
nox.options.stop_on_first_error = True


def get_poetry_dependencies(
    session: nox.Session,
    only: list[str] | None = None,
):
    """Get the dependencies from the poetry.lock file.

    This assumes poetry is installed in the session.

    Arguments:
    ---------
    session : nox.sessions.Session
        The nox session object.

    only : list, optional
        If provided, only return the dependencies that match the provided
        string or strings.

    """
    # "-T" includes top-level dependencies only.
    command = ['poetry', 'show']

    if only:
        command.extend(['--only', ','.join(only)])

    out = session.run(
        *command,
        external=True,
        silent=True,
    )

    if out is None:
        raise ValueError(f'Got no output from "{command}"')

    # Poetry uses (!) to indicate a package is not installed when terminal
    # colors are not available to it (e.g., in a nox session). Need to remove
    # these. They are inconsistent from line to line.
    out = str(out).replace('(!)', '')

    package_strs = out.splitlines()
    package_columns = [line.split() for line in package_strs]
    packages = [
        '=='.join([column[0], column[1]]) for column in package_columns
    ]

    # Log the packages that will be installed.
    session.log(f'Installing the following packages: {packages}')

    return packages


def install_test_dependencies(session: nox.Session):
    """Install the test dependencies from the poetry.lock file."""
    packages = get_poetry_dependencies(session, only=['main', 'test'])
    session.install(*packages)
    session.install('-e', '.')


def dependency_wrapper(func: Callable[[nox.Session], None]):
    """Decorator to install dependencies before running the session."""

    @functools.wraps(func)
    def wrapper(session: nox.Session) -> None:
        install_test_dependencies(session)
        func(session)

    return wrapper


@nox.session(python=TestSettings.python)
@dependency_wrapper
def unit_tests(session: nox.Session):
    _ = session.run(
        'pytest',
        'tests/unit',
        '--cov-append',
        *session.posargs,
        env={'RST_EXTRACT_LOGGING': TestSettings.log_level()},
    )


@nox.session(python=TestSettings.python)
@dependency_wrapper
def integration_tests(session: nox.Session):
    _ = session.run(
        'pytest',
        'tests/integration',
        '--cov-append',
        *session.posargs,
        env={'RST_EXTRACT_LOGGING': TestSettings.log_level()},
    )


@nox.session(python='3.12')
def coverage_report(session: nox.Session):
    session.install('coverage[toml]')
    _ = session.run('coverage', 'report')
    _ = session.run('coverage', 'html')


@nox.session
def devsh(session: nox.Session):
    """Create a development .venv for the project."""
    venv_path = Path('.venv')

    if venv_path.exists():
        session.log('Found existing .venv directory. Removing it.')
        session.run('rm', '-rf', '.venv', external=True)

    session.run('python', '-m', 'venv', str(venv_path.absolute()))
    session.run(
        'bash',
        '-c',
        'source .venv/bin/activate && poetry install',
        external=True,
    )

    session.notify('pre_commit_init')


@nox.session
def pre_commit_init(session: nox.Session):
    """Run pre-commit checks."""
    session.install('pre-commit')
    _ = session.run(
        'pre-commit',
        'install',
        '--install-hooks',
        '-t',
        'pre-commit',
        '-t',
        'commit-msg',
    )


@nox.session(tags=['lint'])
def format(session: nox.Session):
    """Use ruff to format the code."""
    session.install('ruff')
    _ = session.run('ruff', 'format', '.')


@nox.session(tags=['lint'])
def check(session: nox.Session):
    """Use ruff to check the code."""
    session.install('ruff')
    _ = session.run('ruff', 'check', '--fix')
