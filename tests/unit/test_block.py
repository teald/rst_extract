"""Tests for the Block class."""

import os
from pathlib import Path

import pytest
from pydantic import FilePath

from rst_extract.block import Block, BlockError


def test_empty_block() -> None:
    block = Block()
    assert block.code == []
    assert block.offsets == {}
    assert block.path is None
    assert block.directive is None
    assert block.options == tuple()


def test_block_with_code() -> None:
    block = Block(code=['print("Hello, world!")'])
    assert block.code == ['print("Hello, world!")']
    assert block.offsets == {}
    assert block.path is None
    assert block.directive is None
    assert block.options == tuple()


def test_block_with_offsets() -> None:
    block = Block(offsets={1: 3})
    assert block.code == []
    assert block.offsets == {1: 3}
    assert block.path is None
    assert block.directive is None
    assert block.options == tuple()


def test_block_with_path(tmp_path: Path) -> None:
    # Create a temporary file to use as the path
    file = os.path.join(tmp_path, 'file.rst')
    with open(file, 'w+') as f:
        f.write('')

    path = file

    block = Block(path=path)
    assert block.code == []
    assert block.offsets == {}
    assert block.path == FilePath(path)
    assert block.directive is None
    assert block.options == tuple()


def test_block_with_directive() -> None:
    block = Block(directive='code-block')
    assert block.code == []
    assert block.offsets == {}
    assert block.path is None
    assert block.directive == 'code-block'
    assert block.options == tuple()


def test_block_with_options() -> None:
    block = Block(options=('python', 'linenos'))
    assert block.code == []
    assert block.offsets == {}
    assert block.path is None
    assert block.directive is None
    assert block.options == ('python', 'linenos')


def test_block_with_all(tmp_path: Path) -> None:
    path = str(os.path.join(tmp_path, 'file.rst'))

    with open(path, 'w+') as f:
        f.write('')

    block = Block(
        code=['print("Hello, world!")'],
        offsets={1: 3},
        path=path,
        directive='code-block',
        options=['linenos'],
    )

    assert block.code == ['print("Hello, world!")']
    assert block.offsets == {1: 3}
    assert block.path == FilePath(path)
    assert block.directive == 'code-block'
    assert block.options == ('linenos',)


def test_block_from_string(code_block_hello_world_string: str) -> None:
    block = Block.from_string(code_block_hello_world_string)
    assert block.code == ['print("Hello, World!")']
    assert block.offsets == {0: 2}
    assert block.path is None
    assert block.directive == 'code-block'
    assert block.options == tuple()


def test_block_from_string_with_options(
    code_block_hello_world_with_options_string: str,
) -> None:
    block = Block.from_string(code_block_hello_world_with_options_string)
    assert block.code == ['print("Hello, World!")']
    assert block.offsets == {0: 3}
    assert block.path is None
    assert block.directive == 'code-block'
    assert block.options == ('linenos',)


def test_block_with_bad_input() -> None:
    with pytest.raises(BlockError):
        Block.from_string('This is not a code block.')
