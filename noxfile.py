# Ignore mypy for this file, for now
# mypy: ignore-errors
# TODO(teald): Add type hints to this file.
import functools
from typing import Literal

import nox


class TestSettings:
    # Python versions to test against.
    python: list[Literal[str]] = ['3.10', '3.11', '3.12']

    # Nox sessions to run by default.
    sessions: list[Literal[str]] = [
        'unit_tests',
        'integration_tests',
        'coverage_report',
    ]


# These settings are used for local development.
# TODO: Override these in CI.
nox.options.sessions = TestSettings.sessions
nox.options.reuse_existing_virtualenvs = True
nox.options.error_on_missing_interpreters = True
nox.options.stop_on_first_error = True


def get_poetry_dependencies(session, only: str | list[str] = ''):
    """Get the dependencies from the poetry.lock file.

    This assumes poetry is installed in the session.

    Arguments
    ---------
    session : nox.sessions.Session
        The nox session object.

    only : str, list, optional
        If provided, only return the dependencies that match the provided
        string or strings.
    """
    # "-T" includes top-level dependencies only.
    command = ['poetry', 'show']

    if only:
        command.extend(['--only', only])

    out = session.run(
        *command,
        external=True,
        silent=True,
    )

    # Poetry uses (!) to indicate a package is not installed when terminal
    # colors are not available to it (e.g., in a nox session). Need to remove
    # these. They are inconsistent from line to line.
    out = out.replace('(!)', '')

    package_strs = out.splitlines()
    package_columns = [line.split() for line in package_strs]
    packages = ['=='.join([column[0], column[1]]) for column in package_columns]

    return packages


def install_test_dependencies(session):
    """Install the test dependencies from the poetry.lock file."""
    packages = get_poetry_dependencies(session, only='main,test')
    session.install(*packages)


def dependency_wrapper(func):
    """Decorator to install dependencies before running the session."""

    @functools.wraps(func)
    def wrapper(session):
        install_test_dependencies(session)
        result = func(session)

        return result

    return wrapper


@nox.session
def pre_test_clean(session):
    session.run('rm', '-rf', '.coverage', 'htmlcov')
    session.run(
        'find',
        '.',
        '-type',
        'd',
        '-name',
        '__pycache__',
        '-exec',
        'rm',
        '-rf',
        '{}',
        '+',
    )


@nox.session(python=TestSettings.python)
@dependency_wrapper
def unit_tests(session):
    session.install('pytest', 'pytest-cov')
    session.run('pytest', 'tests/unit', '--cov-append', *session.posargs)


@nox.session(python=TestSettings.python)
@dependency_wrapper
def integration_tests(session):
    session.install('pytest', 'pytest-cov')
    session.run('pytest', 'tests/integration', '--cov-append', *session.posargs)


@nox.session(python='3.12')
def coverage_report(session):
    session.install('coverage[toml]')
    session.run('coverage', 'report')
    session.run('coverage', 'html')
