"""Tests for all entrypints modules."""

import re
from io import TextIOWrapper
from pathlib import Path
from typing import Any, Sequence

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
def test_flatten(sequence: Sequence[Any], expected: Sequence[Any]) -> None:
    """Test the flatten function works."""
    result = flatten(sequence)

    assert result == expected


def test_custom_param_type_works_with_dir(test_dir: Path) -> None:
    """Ensure the custom param type can be parsed a directory."""
    param_type = FileOrDir()

    result = param_type.convert(test_dir, None, None)

    for file_ in result:
        assert isinstance(file_, TextIOWrapper)
        assert re.match(r".*file[1-2].py", file_.name)
        file_.close()


def test_custom_param_type_works_with_file(test_dir: Path) -> None:
    """Ensure the custom param type can be parsed a file."""
    param_type = FileOrDir()

    result = param_type.convert(test_dir / "test_file1.py", None, None)

    assert isinstance(result, TextIOWrapper)
    assert re.match(r".*file[1-2].py", result.name)
    result.close()


@pytest.mark.parametrize("filename", ["h.py", "new_dir"])
def test_custom_param_type_with_non_existing_files(
    test_dir: Path, filename: str
) -> None:
    """Ensure an error occurs when a non existing file or dir is parsed."""
    param_type = FileOrDir()

    with pytest.raises(click.BadParameter) as error:
        param_type.convert(test_dir / filename, None, None)

    assert f"{filename}' does not exist" in error.value.args[0]


def test_get_files(test_dir: Path) -> None:
    """Ensure we can get all files recursively from a given directory."""
    result = get_files(str(test_dir))

    assert all(re.match(r".*file[1-2].py", file.name) for file in result)
    for file_path in result:
        file_path.close()
