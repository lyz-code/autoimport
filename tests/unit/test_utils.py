"""Tests for the `utils` module."""

from pathlib import Path
from typing import Callable
from unittest.mock import MagicMock, patch

from autoimport.utils import get_pyproject_path, path_contains_pyproject


class TestContainsPyproject:
    """Tests for the `contains_pyproject` function"""

    def test_pyproject_found(self, create_tmp_file: Callable) -> None:
        """
        Given: a path containing a `pyproject.toml` file,
        When: the `contains_pyproject` function is invoked with the path,
        Then: a `True` is returned
        """
        path = create_tmp_file(filename="pyproject.toml")

        result = path_contains_pyproject(path.parent)

        assert result is True

    def test_pyproject_not_found(self, create_tmp_file: Callable) -> None:
        """
        Given: a path not containing a `pyproject.toml` file,
        When: the `contains_pyproject` function is invoked with the path,
        Then: a `False` is returned
        """
        path = create_tmp_file(filename="foo.toml")

        result = path_contains_pyproject(path.parent)

        assert result is False


class TestGetPyprojectPath:
    """Tests for the `get_pyproject_path`"""

    @patch("autoimport.utils.Path", autospec=True)
    def test_in_current_directory(
        self, mock_path: MagicMock, create_tmp_file: Callable
    ) -> None:
        """
        Given: a `pyproject.toml` file in the `cwd`,
        When: the `get_pyproject_path` function is invoked without a `starting_path`,
        Then: the path to the `pyproject.toml` is returned
        """
        path_to_pyproject = create_tmp_file(filename="pyproject.toml")
        mock_path.cwd.return_value = path_to_pyproject.parent

        result = get_pyproject_path()

        assert result == path_to_pyproject

    def test_in_parent_directory(self, create_tmp_file: Callable) -> None:
        """
        Given: a `pyproject.toml` file in the parent of `cwd`,
        When: the `get_pyproject_path` function is invoked,
        Then: the path to the `pyproject.toml` is returned
        """
        path_to_pyproject = create_tmp_file(filename="pyproject.toml")
        sub_dir = path_to_pyproject / "sub"

        result = get_pyproject_path(sub_dir)

        assert result == path_to_pyproject

    def test_not_found(self) -> None:
        """
        Given: no `pyproject.toml` in the `cwd` or parent dirs,
        When: the `get_pyproject_path` function is invoked,
        Then: `None` is returned
        """
        result = get_pyproject_path(Path("/nowhere"))

        assert result is None

    def test_with_given_path(self, create_tmp_file: Callable) -> None:
        """
        Given: a `pyproject.toml` file in a path,
        When: the `get_pyproject_path` function is invoked with a `starting_path`,
        Then: the path to the `pyproject.toml` is returned
        """
        path_to_pyproject = create_tmp_file(filename="pyproject.toml")

        result = get_pyproject_path(starting_path=path_to_pyproject)

        assert result == path_to_pyproject
