"""Module to hold various utils."""

from pathlib import Path
from typing import Optional

PYPROJECT_FILENAME = "pyproject.toml"


def path_contains_pyproject(path: Path) -> bool:
    """Determine whether a `pyproject.toml` exists in the given path.

    Args:
        path (Path): the path in which to search for the `pyproject.toml`

    Returns:
        A boolean to indicate whether a `pyproject.toml` exists in the given path
    """
    return (path / PYPROJECT_FILENAME).is_file()


def get_pyproject_path(starting_path: Optional[Path] = None) -> Optional[Path]:
    """Search for a `pyproject.toml` by traversing up the tree from a path.

    Args:
        starting_path (Path): an optional path from which to start searching

    Returns:
        The `Path` to the `pyproject.toml` if it exists or `None` if it doesn't
    """
    start: Path = starting_path or Path.cwd()

    for path in [start, *start.parents]:
        if path_contains_pyproject(path):
            return path / PYPROJECT_FILENAME

    return None
