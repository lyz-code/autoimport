"""Tests for all entrypints modules."""

import re
from pathlib import Path
from typing import Sequence

import click
import pytest

from autoimport.entrypoints.cli import FileOrDir, flatten, get_files


@pytest.mark.parametrize(
    ("sequence", "expected"),
    [
        ((1, (2, 3, 4), 5), (1, 2, 3, 4, 5)),
        ([1, 2, 3, [4, 5, 6]], (1, 2, 3, 4, 5, 6)),
        ([["a", "b", "c"], "d"], ("a", "b", "c", "d")),
    ],
)
def test_flatten(sequence: Sequence, expected: Sequence) -> None:
    """Test the flatten function works."""
    result = flatten(sequence)

    assert result == expected


def test_custom_param_type_works_with_dir(test_dir: Path) -> None:
    """Ensure the custom param type can be parsed a directory."""
    param_type = FileOrDir()

    result = param_type.convert(test_dir, None, None)

    assert all(re.match(r".*file[1-2].py", f.name) for f in result)


def test_custom_param_type_works_with_file(test_dir: Path) -> None:
    """Ensure the custom param type can be parsed a file."""
    param_type = FileOrDir()

    result = param_type.convert(test_dir / "test_file1.py", None, None).name

    assert re.match(r".*file[1-2].py", result)


@pytest.mark.parametrize("filename", ["h.py", "new_dir"])
def test_custom_param_type_with_non_existing_files(
    test_dir: Path, filename: str
) -> None:
    """Ensure an error occurs when a non existing file or dir is parsed."""
    param_type = FileOrDir()

    with pytest.raises(click.BadParameter) as e:
        param_type.convert(test_dir / filename, None, None)

    assert f"{filename}' does not exist" in e.value.args[0]


def test_get_files(test_dir: Path) -> None:
    """Ensure we can get all files recursively from a given directory."""
    result = get_files(test_dir)

    assert all(re.match(r".*file[1-2].py", f.name) for f in result)
