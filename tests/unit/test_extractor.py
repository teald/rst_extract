"""Tests for the Extractor class."""
# Ignore type hinting in mypy
# mypy: ignore-errors

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
