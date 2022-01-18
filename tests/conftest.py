"""Store the classes and fixtures used throughout the tests."""

import pathlib

import pytest
from py._path.local import LocalPath


@pytest.fixture()
def test_dir(tmpdir: LocalPath) -> pathlib.Path:
    """Creates test directory and files and returns root test file directory."""
    file_contents = "os.getcwd()"

    test_dirs = pathlib.Path(tmpdir) / "test_files"
    subdir = test_dirs / "subdir"

    subdir.mkdir(parents=True)

    file1 = test_dirs / "test_file1.py"
    with file1.open("w") as f1:
        f1.write(file_contents)

    file2 = subdir / "test_file2.py"
    with file2.open("w") as f2:
        f2.write(file_contents)

    return test_dirs
