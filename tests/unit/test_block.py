"""Tests for the Block class."""

from rst_extract.block import Block


def test_empty_block() -> None:
    block = Block()
    assert block.code == []
    assert block.offsets == {}
    assert block.path is None
    assert block.directive is None
    assert block.options == []
