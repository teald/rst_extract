"""Tests for the Extractor class."""

# Ignore type hinting in mypy
# mypy: ignore-errors
from os.path import join

import pytest
from hypothesis import given
from hypothesis import strategies as st

from rst_extract.extractor import ExtractionError, Extractor

_NUMBER_ST = st.one_of(st.integers(), st.floats())


@given(
    bad_filename=st.one_of(
        _NUMBER_ST,
        st.none(),
        st.tuples(),
        st.lists(_NUMBER_ST),
        st.dictionaries(st.one_of(st.text(), _NUMBER_ST), _NUMBER_ST),
    )
)
def test_extractor_bad_init(bad_filename):
    """Test the Extractor class initialization."""
    from rst_extract.extractor import Extractor

    with pytest.raises(TypeError):
        Extractor(bad_filename)


def test_no_file_found():
    """Test the Extractor class when no file is found."""
    ext = Extractor('/nonexistent_dir/nonexistent_file.rst')

    with pytest.raises(ExtractionError):
        ext.extract()


def test_extract_empty_file(empty_rst):
    """Test the Extractor class when an empty file is found."""
    ext = Extractor('empty_file.rst')

    with pytest.raises(ExtractionError):
        ext.extract()


def test_extract_code_only_file(code_only_rst, code_only_rst_result):
    """Test the Extractor class when a code-only file is found."""
    ext = Extractor(code_only_rst)

    extracted = ext.extract()

    assert extracted == code_only_rst_result


class _CodeBlockLiterals:
    _literal1 = '.. code-block:: python\n    print("Hello, world!")\n'

    _literal1_result = '# Block 1:\n' 'print("Hello, world!")\n'

    _literal2 = (
        '.. code-block:: python\n'
        '    print("Hello, world!")\n'
        '\n'
        '    print("Goodbye, world!")\n'
    )

    _literal2_result = (
        '# Block 1:\n' 'print("Hello, world!")\n' '\n' 'print("Goodbye, world!")\n'
    )

    _literal3 = (
        '.. code-block:: python\n'
        '    print("Hello, world!")\n'
        '\n'
        '    print("Goodbye, world!")\n'
        '\n'
    )

    _literal3_result = (
        '# Block 1:\n' 'print("Hello, world!")\n' '\n' 'print("Goodbye, world!")\n'
    )

    _literal4 = (
        '.. code-block:: python\n'
        '    print("Hello, world!")\n'
        '\n'
        '    print("Goodbye, world!")\n'
        '\n'
        '.. code-block:: python\n'
        '    print("Hello, world!")\n'
    )

    _literal4_result = (
        '# Block 1:\n'
        'print("Hello, world!")\n'
        '\n'
        'print("Goodbye, world!")\n'
        '\n'
        '# Block 2:\n'
        'print("Hello, world!")\n'
    )

    @classmethod
    def literals(cls):
        all_attrs = dir(cls)

        prompt_result = [
            (getattr(cls, attr), getattr(cls, f'{attr}_result'))
            for attr in all_attrs
            if attr.startswith('_literal') and not attr.endswith('_result')
        ]

        return [
            (i, prompt, result)
            for i, (prompt, result) in enumerate(prompt_result, start=1)
        ]


@pytest.mark.parametrize(
    'number, prompt, result',
    _CodeBlockLiterals.literals(),
)
def test_extract_code_blocks_literals(number, prompt, result, tmp_path):
    """Test the Extractor class with code block literals."""
    temp_file = join(tmp_path, f'literal{number}.rst')

    with open(temp_file, 'w+') as f:
        f.write(prompt)

    ext = Extractor(temp_file)

    extracted = ext.extract()

    assert extracted == result
