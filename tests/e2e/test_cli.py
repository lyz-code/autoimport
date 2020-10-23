"""Test the command line interface."""

import re

import pytest
from click.testing import CliRunner

from autoimport.entrypoints.cli import cli
from autoimport.version import __version__


@pytest.fixture(name="runner")
def fixture_runner() -> CliRunner:
    """Configure the Click cli test runner."""
    return CliRunner(mix_stderr=False)


def test_version(runner) -> None:
    """Prints program version when called with --version."""
    result = runner.invoke(cli, ["--version"])

    assert result.exit_code == 0
    assert re.match(
        fr" *repository-pattern version: {__version__}\n"
        r" *python version: .*\n *platform: .*",
        result.stdout,
    )


def test_corrects_one_file(runner, tmpdir) -> None:
    """Correct the source code of a file."""
    test_file = tmpdir.join("source.py")
    test_file.write("os.getcwd()")
    fixed_source = """import os
os.getcwd()"""

    result = runner.invoke(cli, [str(test_file)])

    assert result.exit_code == 0
    assert test_file.read() == fixed_source


@pytest.mark.secondary
def test_corrects_three_file(runner, tmpdir) -> None:
    """Correct the source code of a file."""
    test_files = []
    for file_number in range(3):
        test_file = tmpdir.join(f"source_{file_number}.py")
        test_file.write("os.getcwd()")
        test_files.append(test_file)
    fixed_source = """import os
os.getcwd()"""

    result = runner.invoke(cli, [str(test_file) for test_file in test_files])

    assert result.exit_code == 0
    for test_file in test_files:
        assert test_file.read() == fixed_source


def test_corrects_code_from_stdin(runner) -> None:
    """Correct the source code passed as stdin."""
    source = "os.getcwd()"
    fixed_source = """import os
os.getcwd()
"""

    result = runner.invoke(cli, ["-"], input=source)

    assert result.exit_code == 0
    assert result.stdout == fixed_source


def test_doesnt_touch_correct_code_from_stdin(runner) -> None:
    """Correct source code should not be touched when loaded from stdin."""
    source = """import os

os.getcwd()"""

    result = runner.invoke(cli, ["-"], input=source)

    assert result.exit_code == 0
    assert result.stdout == source
