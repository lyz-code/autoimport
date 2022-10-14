"""Test the command line interface."""

import os
import re
from pathlib import Path
from textwrap import dedent
from typing import Dict, List, Optional

import pytest
from click.testing import CliRunner
from py._path.local import LocalPath

from autoimport.entrypoints.cli import cli
from autoimport.version import __version__


@pytest.fixture(name="runner")
def fixture_runner() -> CliRunner:
    """Configure the Click cli test runner."""
    return CliRunner(mix_stderr=False, env={"XDG_CONFIG_HOME": "/dev/null"})


def test_version(runner: CliRunner) -> None:
    """Prints program version when called with --version."""
    result = runner.invoke(cli, ["--version"])

    assert result.exit_code == 0
    assert re.search(
        rf" *autoimport: {__version__}\n *Python: .*\n *Platform: .*",
        result.stdout,
    )


def test_corrects_one_file(runner: CliRunner, tmpdir: LocalPath) -> None:
    """Correct the source code of a file."""
    test_file = tmpdir / "source.py"
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
        test_file = tmpdir / f"source_{file_number}.py"
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


def test_correct_all_files_in_dir_recursively(
    runner: CliRunner, test_dir: Path
) -> None:
    """Ensure files and dirs can be parsed and fixes associated files."""
    result = runner.invoke(cli, [str(test_dir)])

    assert result.exit_code == 0
    fixed_source = "import os\n\n\nos.getcwd()"
    assert (test_dir / "test_file1.py").read_text() == fixed_source
    assert (test_dir / "subdir/test_file2.py").read_text() == fixed_source


def test_correct_mix_dir_and_files(
    runner: CliRunner, test_dir: Path, tmpdir: LocalPath
) -> None:
    """Ensure all files in a given directory get fixed by autoimport."""
    test_file = tmpdir / "source.py"
    test_file.write("os.getcwd()")

    result = runner.invoke(cli, [str(test_dir), str(test_file)])

    assert result.exit_code == 0
    fixed_source = "import os\n\n\nos.getcwd()"
    assert (test_dir / "test_file1.py").read_text() == fixed_source
    assert (test_dir / "subdir/test_file2.py").read_text() == fixed_source
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
    pyproject_toml = tmpdir / "pyproject.toml"
    pyproject_toml.write(
        dedent(
            """\
            [tool.autoimport]
            common_statements = { "FooBar" = "from baz.qux import FooBar" }
            """
        )
    )
    test_file = tmpdir / "source.py"
    test_file.write("FooBar\n")
    with tmpdir.as_cwd():

        result = runner.invoke(cli, [str(test_file)])

    assert result.exit_code == 0
    assert test_file.read() == dedent(
        """\
        from baz.qux import FooBar


        FooBar
        """
    )


@pytest.mark.skip("Until https://github.com/dbatten5/maison/issues/141 is fixed")
def test_config_path_argument(runner: CliRunner, tmpdir: LocalPath) -> None:
    """Allow common_statements to be defined in pyproject.toml"""
    config_dir = tmpdir / "config"
    config_dir.mkdir()
    pyproject_toml = config_dir / "pyproject.toml"
    pyproject_toml.write(
        dedent(
            """\
            [tool.autoimport]
            common_statements = { "FooBar" = "from baz.qux import FooBar" }
            """
        )
    )
    code_dir = tmpdir / "code"
    code_dir.mkdir()
    test_file = code_dir / "source.py"
    test_file.write("FooBar\n")

    result = runner.invoke(cli, ["--config-file", str(pyproject_toml), str(test_file)])

    assert result.exit_code == 0
    assert test_file.read() == dedent(
        """\
        from baz.qux import FooBar


        FooBar
        """
    )


@pytest.mark.parametrize(
    ("create_global_conf", "use_local_conf", "create_pyproject", "expected_imports"),
    [
        pytest.param(True, False, False, "from g import G", id="global"),
        pytest.param(False, True, False, "from r import R", id="local"),
        pytest.param(False, False, True, "from p import P", id="pyproject"),
        pytest.param(
            True, True, False, "from g import G\nfrom r import R", id="global-and-local"
        ),
        pytest.param(
            True,
            False,
            True,
            "from g import G\nfrom p import P",
            id="global-and-pyproject",
        ),
        pytest.param(
            False,
            True,
            True,
            "from r import R\nfrom p import P",
            id="local-and-pyproject",
        ),
        pytest.param(
            True,
            True,
            True,
            "from g import G\nfrom r import R\nfrom p import P",
            id="global-and-local-and-pyproject",
        ),
    ],
)
# R0913: Too many arguments (6/5): We need to refactor this test in many more
def test_global_and_local_config(  # noqa: R0913
    runner: CliRunner,
    tmpdir: LocalPath,
    create_global_conf: bool,
    use_local_conf: bool,
    create_pyproject: bool,
    expected_imports: str,
) -> None:
    """
    Test interaction between the following:
      - presence of the global config file $XDG_CONFIG_HOME/autoimport/config.toml
      - use of the --config-file flag to specify a local config file
      - presence of a pyproject.toml file
    """
    config = {
        "global": '[common_statements]\n"G" = "from g import G"',
        "local": '[common_statements]\n"R" = "from r import R"',
        "pyproject": '[tool.autoimport.common_statements]\n"P" = "from p import P"',
    }
    code_path = tmpdir / "code.py"
    original_code = dedent(
        """
        G
        R
        P
        """
    )
    code_path.write(original_code)
    args: List[str] = [str(code_path)]
    env: Dict[str, Optional[str]] = {}
    if create_global_conf:
        # must be absolute path
        env["XDG_CONFIG_HOME"] = str(Path(tmpdir / "xdg_home").resolve())
        global_conf_path = tmpdir / "xdg_home" / "autoimport" / "config.toml"
        global_conf_path.ensure()
        global_conf_path.write(config["global"])
    if use_local_conf:
        local_conf_path = tmpdir / "cfg" / "local.toml"
        local_conf_path.ensure()
        local_conf_path.write(config["local"])
        args.extend(["--config-file", str(local_conf_path)])
    if create_pyproject:
        pyproject_path = tmpdir / "pyproject.toml"
        pyproject_path.write(config["pyproject"])
    with tmpdir.as_cwd():

        result = runner.invoke(cli, args, env=env)

    assert result.exit_code == 0
    assert code_path.read() == expected_imports + "\n\n" + original_code


def test_global_and_local_config_precedence(
    runner: CliRunner, tmpdir: LocalPath
) -> None:
    """
    Test precedence of configuration specified in the global config vs
    pyproject.toml vs --config-file. From low to high priority:
      - global config file
      - project-local pyproject.toml file
      - file specified by the --config-file flag, if any
    """
    conf_global = dedent(
        """
        [common_statements]
        "G" = "from g import G"
        "A" = "from ga import A"
        "B" = "from gb import B"
        "C" = "from gc import C"
        """
    )
    conf_pyproject = dedent(
        """
        [tool.autoimport.common_statements]
        "A" = "from pa import A"
        "C" = "from pc import C"
        "D" = "from pd import D"
        """
    )
    conf_local = dedent(
        """
        [common_statements]
        "B" = "from lb import B"
        "C" = "from lc import C"
        "D" = "from ld import D"
        """
    )
    code_path = tmpdir / "code.py"
    original_code = dedent(
        """
        A
        B
        C
        D
        G
        """
    )
    expected_imports = dedent(
        """\
        from pa import A
        from lb import B
        from lc import C
        from ld import D
        from g import G
        """
    )
    code_path.write(original_code)
    args: List[str] = [str(code_path)]
    env: Dict[str, Optional[str]] = {}
    # create_global_conf:
    xdg_home = tmpdir / "xdg_home"
    env["XDG_CONFIG_HOME"] = str(Path(xdg_home).resolve())  # must be absolute path
    global_conf_path = xdg_home / "autoimport" / "config.toml"
    global_conf_path.ensure()
    global_conf_path.write(conf_global)
    # use_local_conf:
    local_conf_path = tmpdir / "cfg" / "local.toml"
    local_conf_path.ensure()
    local_conf_path.write(conf_local)
    args.extend(["--config-file", str(local_conf_path)])
    # create_pyproject:
    pyproject_path = tmpdir / "pyproject.toml"
    pyproject_path.write(conf_pyproject)
    with tmpdir.as_cwd():

        result = runner.invoke(cli, args, env=env)

    assert result.exit_code == 0
    assert code_path.read() == expected_imports + "\n" + original_code


def test_fix_files_doesnt_touch_the_file_if_its_not_going_to_change_it(
    runner: CliRunner, tmpdir: LocalPath
) -> None:
    """
    Given: A file that doesn't need any change
    When: fix files is run
    Then: The file is untouched
    """
    test_file = tmpdir / "source.py"
    test_file.write("a = 1")
    modified_time = os.path.getmtime(test_file)

    result = runner.invoke(cli, [str(test_file)])

    assert result.exit_code == 0
    assert os.path.getmtime(test_file) == modified_time
