"""Tests for the validation class.

TODO(teald):
- [x] validator = Validator()
- [x] bool(validator) -> True
- [ ] bool(validator) -> False for invalid python code.
    - [x] For syntax errors
    - [ ] For undefined names/variables in the code
- [ ] bool(validator)
"""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from rst_extract import Validator


def test_validator() -> None:
    """Test the validator class."""
    validator = Validator()
    assert bool(validator) is True


@pytest.mark.parametrize(
    'code',
    [
        'print("Hello, World!")',
        'import os',
        '',
        'def my_function(): ...',
        'class MyClass:\n\tpass',
        'class MyClass:\n\tpass\n\n',
        'blah, y = 1, 2',
        'blah, y = 1, 2\n',
        'blah, y = 1, 2\n\n',
    ],
)
def test_validator_valid_code(code: str) -> None:
    validator = Validator(code=code)
    assert bool(validator) is True


@pytest.mark.parametrize(
    'bad_code',
    [
        # These should be simple strings that are *not* valid python code.
        'print("Hello, World!)\n',
        'print"Hello, World!")\n',
        'print("Hello, World!"\n',
        'def blach():\n',
        'class MyClass:\n',
        'cast cast cast',
        'import',
    ],
)
def test_validator_invalid_code(bad_code: str) -> None:
    validator = Validator(code=bad_code)
    assert bool(validator) is False


@given(
    st.from_regex(r'^[a-zA-Z][a-zA-Z0-9]*$', fullmatch=True),
)
def test_validator_hypothesis_invalid_name(bad_code: str) -> None:
    # Ignore some special Python keywords that are syntax errors on their own.
    if bad_code in {'in', 'or', 'and'}:
        return

    # These should *not* be caught as invalid Python code; this idea was
    # floated for a bit and discarded. NameErrors are caught at execution time.
    validator = Validator(code=bad_code)
    assert bool(validator) is True
