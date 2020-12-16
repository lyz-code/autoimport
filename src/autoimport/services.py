"""Gather all the orchestration functionality required by the program to work.

Classes and functions that connect the different domain model objects with the adapters
and handlers to achieve the program's purpose.
"""

import importlib
import re
import typing
from typing import Dict, List, Optional, Tuple

import autoflake
import pyflakes
from _io import TextIOWrapper

common_statements: Dict[str, str] = {
    "BeautifulSoup": "from bs4 import BeautifulSoup",
    "call": "from unittest.mock import call",
    "CaptureFixture": "from _pytest.capture import CaptureFixture",
    "CliRunner": "from click.testing import CliRunner",
    "copyfile": "from shutil import copyfile",
    "dedent": "from textwrap import dedent",
    "LocalPath": "from py._path.local import LocalPath",
    "LogCaptureFixture": "from _pytest.logging import LogCaptureFixture",
    "Mock": "from unittest.mock import Mock",
    "patch": "from unittest.mock import patch",
    "StringIO": "from io import StringIO",
    "TempdirFactory": "from _pytest.tmpdir import TempdirFactory",
    "YAMLError": "from yaml import YAMLError",
}


def fix_files(files: Tuple[TextIOWrapper]) -> Optional[str]:
    """Fix the python source code of a list of files.

    If the input is taken from stdin, it will output the value to stdout.

    Args:
        files: List of files to fix.

    Returns:
        Fixed code retrieved from stdin or None.
    """
    for file_wrapper in files:
        source = file_wrapper.read()
        fixed_source = fix_code(source)

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


def fix_code(source_code: str, aliases: Optional[Dict[str, str]] = None) -> str:
    """Fix python source code to correct import statements.

    It corrects these errors:

        * Add missed import statements.
        * Remove unused import statements.
        * Move import statements to the top.

    Args:
        source_code: Source code to be corrected.
        aliases: User defined import lines accessed by object name.

    Returns:
        Corrected source code.
    """
    source_code = _fix_flake_import_errors(source_code, aliases)
    source_code = _move_imports_to_top(source_code)

    return source_code


def _fix_flake_import_errors(
    source_code: str, aliases: Optional[Dict[str, str]] = None
) -> str:
    """Fix python source code to correct missed or unused import statements.

    Args:
        source_code: Source code to be corrected.
        aliases: User defined import lines accessed by object name.

    Returns:
        Corrected source code.
    """
    error_messages = autoflake.check(source_code)

    for message in error_messages:
        if isinstance(message, pyflakes.messages.UndefinedName):
            object_name = message.message_args[0]

            # Try to load the import_string from the aliases first.
            if aliases is not None:
                try:
                    import_string: Optional[str] = aliases[object_name]
                except KeyError:
                    import_string = _find_package(object_name)
            else:
                import_string = _find_package(object_name)

            if import_string is not None:
                source_code = _add_package(source_code, import_string)
        elif isinstance(message, pyflakes.messages.UnusedImport):
            import_name = message.message_args[0]
            line_number = message.lineno
            source_code = _remove_unused_imports(source_code, import_name, line_number)

    return source_code


def _find_package(name: str) -> Optional[str]:
    """Search package by an object's name.

    It will search in these places:

    * Modules in PYTHONPATH.
    * Typing library.

    Args:
        name: Object name to search.

    Returns:
        import_string: String required to import the package.
    """
    for check in [
        _find_package_in_modules,
        _find_package_in_typing,
        _find_package_in_common_statements,
    ]:
        package = check(name)
        if package is not None:
            return package
    return None


def _find_package_in_modules(name: str) -> Optional[str]:
    """Search in the PYTHONPATH modules if object is a package.

    Args:
        name: package name

    Returns:
        import_string: String required to import the package.
    """
    package_specs = importlib.util.find_spec(name)  # type: ignore

    try:
        importlib.util.module_from_spec(package_specs)  # type: ignore

    except AttributeError:
        return None

    return f"import {name}"


def _find_package_in_typing(name: str) -> Optional[str]:
    """Search in the typing library the object name.

    Args:
        name: package name

    Returns:
        import_string: Python 3.7 type checking compatible import string.
    """
    typing_objects = dir(typing)

    # Clean the internal objects (started with _ or __)
    typing_objects = [obj for obj in typing_objects if not re.match("^_.*", obj)]

    if name in typing_objects:
        return f"from typing import {name}"

    return None


def _find_package_in_common_statements(name: str) -> Optional[str]:
    """Search in the common statements the object name.

    Args:
        name: package name

    Returns:
        import_string
    """
    if name in common_statements.keys():
        return common_statements[name]

    return None


def _add_package(source_code: str, import_string: str) -> str:
    """Add a package to the source code.

    Args:
        import_string: string required to import the package.
        source_code: Source code to be corrected.

    Returns:
        fixed_source_code: Source code with package added.
    """
    docstring_lines, import_lines, code_lines = _split_code(source_code)
    import_lines.append(import_string)

    return _join_code(docstring_lines, import_lines, code_lines)


def _split_code(source_code: str) -> Tuple[List[str], List[str], List[str]]:
    """Split the source code in docstring, import statements and code.

    Args:
        source_code: Source code to be corrected.

    Returns:
        docstring_lines: Lines that contain the file docstring.
        import_lines: Lines that contain the import statements.
        code_lines: The rest of lines.
    """
    source_code_lines = source_code.splitlines()
    docstring_lines: List["str"] = []
    docstring_type: Optional[str] = None

    # Extract the module docstring from the code.
    for line in source_code_lines:
        if re.match(r'"{3}.*"{3}', line):
            # Match single line docstrings
            docstring_lines.append(line)
            break
        if docstring_type == "start_multiple_lines" and re.match(r'""" ?', line):
            # Match end of multiple line docstrings
            docstring_type = "multiple_lines"
        elif re.match(r'"{3}.*', line):
            # Match multiple line docstrings start
            docstring_type = "start_multiple_lines"
        elif docstring_type in [None, "multiple_lines"]:
            break
        docstring_lines.append(line)

    # Extract the import lines from the code.
    import_lines: List["str"] = []
    import_start_line = len(docstring_lines)
    multiline_import = False

    for line in source_code_lines[import_start_line:]:
        if (
            re.match(r"^\s*(from .*)?import.[^\'\"]*$", line)
            or line == ""
            or multiline_import
        ):
            # Process multiline import statements
            if "(" in line:
                multiline_import = True
            elif ")" in line:
                multiline_import = False
            import_lines.append(line)
        else:
            break

    # Extract the code lines
    code_start_line = len(docstring_lines) + len(import_lines)
    code_lines = source_code_lines[code_start_line:]

    return docstring_lines, import_lines, code_lines


def _join_code(
    docstring_lines: List[str], import_lines: List[str], code_lines: List[str]
) -> str:
    """Join the source code from docstring, import statements and code lines.

    Make sure that an empty line splits them.

    Args:
        docstring_lines: Lines that contain the file docstring.
        import_lines: Lines that contain the import statements.
        code_lines: The rest of lines.

    Returns:
        source_code: Source code to be corrected.
    """
    # Remove new lines at start and end of each section
    for section in (docstring_lines, import_lines, code_lines):
        for index in (0, -1):
            if len(section) > 0 and section[index] == "":
                section.pop(index)

    # Add new lines between existent sections
    for section in (docstring_lines, import_lines):
        if len(section) > 0 and section[-1] != "":
            section.append("")

    return "\n".join(docstring_lines + import_lines + code_lines)


def _remove_unused_imports(source_code: str, import_name: str, line_number: int) -> str:
    """Remove unused import statements.

    Args:
        source_code: Source code to be corrected.
        import_name: Name of the imported object.

    Returns:
        fixed_source_code: Corrected source code.
    """
    source_code_lines = source_code.splitlines()
    line_number -= 1
    package_name = ".".join(import_name.split(".")[:-1])
    object_name = import_name.split(".")[-1]

    # If it's the only line, remove it
    if re.match(
        fr"(from {package_name} )?import {object_name}$", source_code_lines[line_number]
    ):
        source_code_lines.pop(line_number)
    # If it shares the line with other objects, just remove the unused one.
    elif re.match(
        fr"from {package_name} import .*?{object_name}", source_code_lines[line_number]
    ):
        match = re.match(
            fr"(?P<from>from {package_name} import) (?P<imports>.*)",
            source_code_lines[line_number],
        )
        if match is not None:
            imports = match["imports"].split(", ")
            imports.remove(object_name)
            new_imports = ", ".join(imports)
            source_code_lines[line_number] = f"{match['from']} {new_imports}"
    # If it's a multiline import statement
    # fmt: off
    # Format is required until there is no more need of the
    # experimental-string-processing flag of the Black formatter.
    elif re.match(
        fr"from {package_name} import .*?\($",
        source_code_lines[line_number],
    ):
        # fmt: on
        while line_number + 1 < len(source_code_lines):
            line_number += 1
            if re.match(fr"\s*?{object_name},?", source_code_lines[line_number]):
                source_code_lines.pop(line_number)

    fixed_source_code: str = "\n".join(source_code_lines)

    return fixed_source_code


def _move_imports_to_top(source_code: str) -> str:
    """Fix python source code to move import statements to the top of the file.

    Ignore the lines that contain the # noqa: autoimport string.

    Args:
        source_code: Source code to be corrected.

    Returns:
        Corrected source code.
    """
    docstring_lines, import_lines, code_lines = _split_code(source_code)
    multiline_import = False
    multiline_string = False

    for line in code_lines:
        # Process multiline strings, taking care not to catch single line strings
        # defined with three quotes.
        if re.match(r"^.*?(\"|\'){3}.*?(?!\1{3})$", line) and not re.match(
            r"^.*?(\"|\'){3}.*?\1{3}", line
        ):
            multiline_string = not multiline_string
            continue

        # Process import lines
        if (
            "=" not in line
            and not multiline_string
            and re.match(r"^\s*(?:from .*)?import .[^\'\"]*$", line)
        ) or multiline_import:
            # Ignore the lines containing # noqa: autoimport
            if re.match(r".*?# ?noqa:.*?autoimport.*", line):
                continue

            # Process multiline import statements
            if "(" in line:
                multiline_import = True
            elif ")" in line:
                multiline_import = False

            import_lines.append(line.strip())
            code_lines.remove(line)

    return _join_code(docstring_lines, import_lines, code_lines)
