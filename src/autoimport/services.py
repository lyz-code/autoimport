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


def fix_code(source_code: str, aliases: Optional[Dict[str, str]] = None) -> str:
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


def _remove_unused_imports(source_code: str, import_name: str, line_number: int) -> str:
    """Change python source code to remove unused imports.

    Args:
        source_code: Source code to be corrected.
        import_name: Name of the imported object.

    Returns:
        fixed_source_code: Corrected source code.
    """
    program_lines = source_code.splitlines()
    line_number -= 1
    package_name = ".".join(import_name.split(".")[:-1])
    object_name = import_name.split(".")[-1]

    # If it's the only line, remove it
    if re.match(
        fr"(from {package_name} )?import {object_name}$", program_lines[line_number]
    ):
        program_lines.pop(line_number)
    # If it shares the line with other objects, just remove the unused one.
    elif re.match(
        fr"from {package_name} import .*?{object_name}", program_lines[line_number]
    ):
        match = re.match(
            fr"(?P<from>from {package_name} import) (?P<imports>.*)",
            program_lines[line_number],
        )
        if match is not None:
            imports = match["imports"].split(", ")
            imports.remove(object_name)
            new_imports = ", ".join(imports)
            program_lines[line_number] = f"{match['from']} {new_imports}"

    fixed_source_code: str = "\n".join(program_lines)

    return fixed_source_code


def _add_package(source_code: str, import_string: str) -> str:
    """Add a package to the source code.

    Args:
        import_string: string required to import the package.
        source_code: Source code to be corrected.

    Returns:
        fixed_source_code: Source code with package added.
    """
    docstring_lines, code_lines = _extract_docstring(source_code)
    fixed_source_code_lines = docstring_lines + import_string.splitlines() + code_lines
    fixed_source_code: str = "\n".join(fixed_source_code_lines)

    return fixed_source_code


def _extract_docstring(source_code: str) -> Tuple[List[str], List[str]]:
    """Split the source code in docstring and code.

    Args:
        source_code: Source code to be corrected.

    Returns:
        docstring_lines: Lines that contain the file docstring.
        code_lines: The rest of lines.
    """
    program_lines = source_code.splitlines()
    docstring_lines: List["str"] = []
    has_docstring = False

    for line in program_lines:
        if has_docstring and re.match(r'""" ?', line):
            has_docstring = False
        elif re.match(r'"{3}.*', line):
            has_docstring = True
        elif not has_docstring:
            break
        docstring_lines.append(line)

    code_start_line = len(docstring_lines)
    code_lines = program_lines[code_start_line:]

    return docstring_lines, code_lines


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
    for check in [_find_package_in_modules, _find_package_in_typing]:
        package = check(name)
        if package is not None:
            return package
    return None


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
