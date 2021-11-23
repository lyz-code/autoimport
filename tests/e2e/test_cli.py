"""Test the command line interface."""

import re
from textwrap import dedent

import pytest
from click.testing import CliRunner
from py._path.local import LocalPath

from autoimport.entrypoints.cli import cli
from autoimport.version import __version__


@pytest.fixture(name="runner")
def fixture_runner() -> CliRunner:
    """Configure the Click cli test runner."""
    return CliRunner(mix_stderr=False)


def test_version(runner: CliRunner) -> None:
    """Prints program version when called with --version."""
    result = runner.invoke(cli, ["--version"])

    assert result.exit_code == 0
    assert re.match(
        fr" *autoimport version: {__version__}\n"
        r" *python version: .*\n *platform: .*",
        result.stdout,
    )


def test_corrects_one_file(runner: CliRunner, tmpdir: LocalPath) -> None:
    """Correct the source code of a file."""
    test_file = tmpdir.join("source.py")  # type: ignore
    test_file.write("os.getcwd()")
    fixed_source = dedent(
        """\
        import os

        os.getcwd()"""
    )

    result = runner.invoke(cli, [str(test_file)])

    assert result.exit_code == 0
    assert test_file.read() == fixed_source


@pytest.mark.secondary()
def test_corrects_three_files(runner: CliRunner, tmpdir: LocalPath) -> None:
    """Correct the source code of multiple files."""
    test_files = []
    for file_number in range(3):
        test_file = tmpdir.join(f"source_{file_number}.py")  # type: ignore
        test_file.write("os.getcwd()")
        test_files.append(test_file)
    fixed_source = dedent(
        """\
        import os

        os.getcwd()"""
    )

    result = runner.invoke(cli, [str(test_file) for test_file in test_files])

    assert result.exit_code == 0
    for test_file in test_files:
        assert test_file.read() == fixed_source


def test_corrects_code_from_stdin(runner: CliRunner) -> None:
    """Correct the source code passed as stdin."""
    source = "os.getcwd()"
    fixed_source = dedent(
        """\
        import os

        os.getcwd()"""
    )

    result = runner.invoke(cli, ["-"], input=source)

    assert result.exit_code == 0
    assert result.stdout == fixed_source


def test_pyproject_common_statements(runner: CliRunner, tmpdir: LocalPath) -> None:
    """Allow common_statements to be defined in pyproject.toml"""
    pyproject_toml = tmpdir.join("pyproject.toml")  # type: ignore
    pyproject_toml.write(
        dedent(
            """\
            [tool.autoimport]
            common_statements = { "FooBar" = "from baz_qux import FooBar" }
            """
        )
    )
    test_file = tmpdir.join("source.py")  # type: ignore
    test_file.write("FooBar\n")
    fixed_source = dedent(
        """\
        from baz_qux import FooBar

        FooBar
        """
    )
    with tmpdir.as_cwd():

        result = runner.invoke(cli, [str(test_file)])

    assert result.exit_code == 0
    assert test_file.read() == fixed_source
