"""Gather all the orchestration functionality required by the program to work.

Classes and functions that connect the different domain model objects with the adapters
and handlers to achieve the program's purpose.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from _io import TextIOWrapper
from maison.config import ProjectConfig

from autoimport.model import SourceCode

# To consider: use `xdg.xdg_config_home() / "autoimport" / "config.toml"`
GLOBAL_CONFIG_PATH = "~/.config/autoimport/config.toml"
CONFIG_PROJECT_NAME = "autoimport"


def _read_single_config(config_paths: Optional[List[str]] = None) -> Dict[str, Any]:
    return ProjectConfig(
        project_name=CONFIG_PROJECT_NAME,
        source_files=config_paths,
    ).to_dict()


def deep_updated(target: Dict[str, Any], source: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursive non-mutating `target.update(source)`.

    >>> target = dict(things=dict(a=1, b=2))
    >>> deep_updated(target, dict(things=dict(b=22, c=33), other_things=44))
    {'things': {'a': 1, 'b': 22, 'c': 33}, 'other_things': 44}
    >>> target
    {'things': {'a': 1, 'b': 2}}
    """
    target = target.copy()
    for key, value in source.items():
        if isinstance(value, dict):
            target[key] = deep_updated(target.get(key) or {}, value)
        else:
            target[key] = value
    return target


def read_configs(
    config_file: Optional[str] = None,
    no_global_config: bool = False,
) -> Dict[str, Any]:
    """Read configuration files with semantics corresponding to the CLI options."""
    if not no_global_config:
        global_config_full_path = str(Path(GLOBAL_CONFIG_PATH).expanduser())
        global_config = _read_single_config([global_config_full_path])
    else:
        global_config = {}
    local_config = _read_single_config([config_file] if config_file else None)
    return deep_updated(global_config, local_config)


def fix_files(
    files: Tuple[TextIOWrapper], config: Optional[Dict[str, Any]] = None
) -> Optional[str]:
    """Fix the python source code of a list of files.

    If the input is taken from stdin, it will output the value to stdout.

    Args:
        files: List of files to fix.

    Returns:
        Fixed code retrieved from stdin or None.
    """
    for file_wrapper in files:
        source = file_wrapper.read()
        fixed_source = fix_code(source, config)

        try:
            # Click testing runner doesn't simulate correctly the reading from stdin
            # instead of setting the name attribute to `<stdin>` it gives an
            # AttributeError. But when you use it outside testing, no AttributeError
            # is raised and name has the value <stdin>. So there is no way of testing
            # this behaviour.
            if file_wrapper.name == "<stdin>":  # pragma no cover
                output = "output"
            else:
                output = "file"
        except AttributeError:
            output = "output"

        if output == "file":
            file_wrapper.seek(0)
            file_wrapper.write(fixed_source)
            file_wrapper.truncate()
        else:
            return fixed_source

    return None


def fix_code(original_source_code: str, config: Optional[Dict[str, Any]] = None) -> str:
    """Fix python source code to correct import statements.

    It corrects these errors:

        * Add missed import statements.
        * Remove unused import statements.
        * Move import statements to the top.

    Args:
        original_source_code: Source code to be corrected.

    Returns:
        Corrected source code.
    """
    return SourceCode(original_source_code, config=config).fix()
