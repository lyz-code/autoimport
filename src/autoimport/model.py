"""Define the entities."""

import importlib.util
import inspect
import os
import re
from typing import Dict, List, Optional

import autoflake
from pyflakes.messages import UndefinedExport, UndefinedName, UnusedImport
from pyprojroot import here

common_statements: Dict[str, str] = {
    "BeautifulSoup": "from bs4 import BeautifulSoup",
    "call": "from unittest.mock import call",
    "CaptureFixture": "from _pytest.capture import CaptureFixture",
    "CliRunner": "from click.testing import CliRunner",
    "copyfile": "from shutil import copyfile",
    "dedent": "from textwrap import dedent",
    "FrozenDateTimeFactory": "from freezegun.api import FrozenDateTimeFactory",
    "LocalPath": "from py._path.local import LocalPath",
    "LogCaptureFixture": "from _pytest.logging import LogCaptureFixture",
    "Mock": "from unittest.mock import Mock",
    "patch": "from unittest.mock import patch",
    "StringIO": "from io import StringIO",
    "suppress": "from contextlib import suppress",
    "TempdirFactory": "from _pytest.tmpdir import TempdirFactory",
    "YAMLError": "from yaml import YAMLError",
}


# R0903: Too few public methods (1/2). We don't need more, but using the class instead
#   of passing the data between function calls is useful.
class SourceCode:  # noqa: R090
    """Python source code entity."""

    def __init__(self, source_code: str) -> None:
        """Initialize the object."""
        self.docstring: List[str] = []
        self.imports: List[str] = []
        self.typing: List[str] = []
        self.code: List[str] = []
        self._split_code(source_code)

    def fix(self) -> str:
        """Fix python source code to correct import statements.

        It corrects these errors:

            * Add missed import statements.
            * Remove unused import statements.
            * Move import statements to the top.
        """
        self._move_imports_to_top()
        self._fix_flake_import_errors()

        return self._join_code()

    def _split_code(self, source_code: str) -> None:
        """Split the source code in the different sections.

        * Module Docstring
        * Import statements
        * Typing statements
        * Code.

        Args:
            source_code: Source code to be corrected.
        """
        source_code_lines = source_code.splitlines()

        self._extract_docstring(source_code_lines)
        self._extract_import_statements(source_code_lines)
        self._extract_typing_statements(source_code_lines)
        self._extract_code(source_code_lines)

    def _extract_docstring(self, source_lines: List[str]) -> None:
        """Save the module docstring from the source code into self.docstring.

        Args:
            source_lines: A list containing all code lines.
        """
        docstring_type: Optional[str] = None

        for line in source_lines:
            if re.match(r'"{3}.*"{3}', line):
                # Match single line docstrings
                self.docstring.append(line)
                break
            if docstring_type == "start_multiple_lines" and re.match(r'""" ?', line):
                # Match end of multiple line docstrings
                docstring_type = "multiple_lines"
            elif re.match(r'"{3}.*', line):
                # Match multiple line docstrings start
                docstring_type = "start_multiple_lines"
            elif docstring_type in [None, "multiple_lines"]:
                break
            self.docstring.append(line)

    def _extract_import_statements(self, source_lines: List[str]) -> None:
        """Save the import statements from the source code into self.imports.

        Args:
            source_lines: A list containing all code lines.
        """
        import_start_line = len(self.docstring)
        multiline_import = False
        try_line: Optional[str] = None

        for line in source_lines[import_start_line:]:
            if re.match(r"^if TYPE_CHECKING:$", line):
                break
            if re.match(r"^(try|except.*):$", line):
                try_line = line
            elif (
                re.match(r"^\s*(from .*)?import.[^\'\"]*$", line)
                or line == ""
                or multiline_import
            ):
                # Process multiline import statements
                if "(" in line:
                    multiline_import = True
                elif ")" in line:
                    multiline_import = False

                if try_line:
                    self.imports.append(try_line)
                    try_line = None

                self.imports.append(line)
            else:
                break

    def _extract_typing_statements(self, source_lines: List[str]) -> None:
        """Save the typing statements from the source code into self.typing.

        Args:
            source_lines: A list containing all code lines.
        """
        typing_start_line = len(self.docstring) + len(self.imports)

        if re.match(r"^if TYPE_CHECKING:$", source_lines[typing_start_line]):
            self.typing.append(source_lines[typing_start_line])
            typing_start_line += 1
            for line in source_lines[typing_start_line:]:
                if not re.match(r"^\s+.*", line):
                    break
                self.typing.append(line)

    def _extract_code(self, source_lines: List[str]) -> None:
        """Save the code from the source code into self.code.

        Args:
            source_lines: A list containing all code lines.
        """
        # Extract the code lines
        code_start_line = len(self.docstring) + len(self.imports) + len(self.typing)
        self.code = source_lines[code_start_line:]

    def _join_code(self) -> str:
        """Join the source code from docstring, import statements and code lines.

        Make sure that an empty line splits them.

        Returns:
            source_code: Source code to be corrected.
        """
        # Remove new lines at start and end of each section.
        sections = [
            "\n".join(section).strip()
            for section in (self.docstring, self.imports, self.typing, self.code)
            if len(section) > 0
        ]

        # Add new lines between existent sections
        return "\n\n".join(sections).strip()

    def _move_imports_to_top(self) -> None:
        """Fix python source code to move import statements to the top of the file.

        Ignore the lines that contain the # noqa: autoimport string.
        """
        multiline_import = False
        multiline_string = False
        code_lines_to_remove = []

        for line in self.code:
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

                code_lines_to_remove.append(line)
                if not multiline_import:
                    line = line.strip()

                self.imports.append(line)

        for line in code_lines_to_remove:
            self.code.remove(line)

    def _fix_flake_import_errors(self) -> None:
        """Fix python source code to correct missed or unused import statements."""
        error_messages = autoflake.check(self._join_code())

        for message in error_messages:
            if isinstance(message, (UndefinedName, UndefinedExport)):
                object_name = message.message_args[0]
                self._add_package(object_name)
            elif isinstance(message, UnusedImport):
                import_name = message.message_args[0]
                self._remove_unused_imports(import_name)

    def _add_package(self, object_name: str) -> None:
        """Add a package to the source code.

        Args:
            object_name: Object name to search.
        """
        import_string = self._find_package(object_name)

        if import_string is not None:
            self.imports.append(import_string)

    def _find_package(self, name: str) -> Optional[str]:
        """Search package by an object's name.

        It will search in these places:

        * In the package we are developing.
        * Modules in PYTHONPATH.
        * Typing library.
        * Common statements.

        Args:
            name: Object name to search.

        Returns:
            import_string: String required to import the package.
        """
        for check in [
            "_find_package_in_modules",
            "_find_package_in_typing",
            "_find_package_in_common_statements",
            "_find_package_in_our_project",
        ]:
            package = getattr(self, check)(name)
            if package is not None:
                return package
        return None

    @staticmethod
    def _find_package_in_our_project(name: str) -> Optional[str]:
        """Search the name in the objects of the package we are developing.

        Args:
            name: package name

        Returns:
            import_string: String required to import the package.
        """
        # Find the package name
        project_package = os.path.basename(here()).replace("-", "_")
        package_objects = extract_package_objects(project_package)

        # nocover: as the tests are run inside the autoimport virtualenv, it will
        # always find the objects on that package
        if package_objects is None:  # pragma: nocover
            return None
        try:
            return package_objects[name]
        except KeyError:
            return None

    @staticmethod
    def _find_package_in_modules(name: str) -> Optional[str]:
        """Search in the PYTHONPATH modules if object is a package.

        Args:
            name: package name

        Returns:
            import_string: String required to import the package.
        """
        package_specs = importlib.util.find_spec(name)

        try:
            importlib.util.module_from_spec(package_specs)  # type: ignore
        except AttributeError:
            return None

        return f"import {name}"

    @staticmethod
    def _find_package_in_typing(name: str) -> Optional[str]:
        """Search in the typing library the object name.

        Args:
            name: package name

        Returns:
            import_string: Python 3.7 type checking compatible import string.
        """
        typing_objects = extract_package_objects("typing")

        try:
            return typing_objects[name]
        except KeyError:
            return None

    @staticmethod
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

    def _remove_unused_imports(self, import_name: str) -> None:
        """Remove unused import statements.

        Args:
            import_name: Name of the imported object.
        """
        package_name = ".".join(import_name.split(".")[:-1])
        object_name = import_name.split(".")[-1]

        for line in self.imports:
            # If it's the only line, remove it
            if re.match(fr"(from {package_name} )?import {object_name}$", line):
                self.imports.remove(line)
                return
            # If it shares the line with other objects, just remove the unused one.
            if re.match(fr"from {package_name} import .*?{object_name}", line):
                # fmt: off
                # Format is required until there is no more need of the
                # experimental-string-processing flag of the Black formatter.
                match = re.match(
                    fr"(?P<from>from {package_name} import) (?P<imports>.*)",
                    line,
                )
                # fmt: on
                if match is not None:
                    line_number = self.imports.index(line)
                    imports = match["imports"].split(", ")
                    imports.remove(object_name)
                    new_imports = ", ".join(imports)
                    self.imports[line_number] = f"{match['from']} {new_imports}"
                    return
            # If it's a multiline import statement
            # fmt: off
            # Format is required until there is no more need of the
            # experimental-string-processing flag of the Black formatter.
            elif re.match(
                fr"from {package_name} import .*?\($",
                line,
            ):
                # fmt: on
                line_number = self.imports.index(line)
                while line_number + 1 < len(self.imports):
                    line_number += 1
                    if re.match(fr"\s*?{object_name},?", self.imports[line_number]):
                        self.imports.pop(line_number)
                        return


def extract_package_objects(name: str) -> Dict[str, str]:
    """Extract the package objects and their import string.

    Returns:
        objects: A dictionary with the object name as a key and the import string
            as the value.
    """
    package_objects: Dict[str, str] = {}
    package_modules = []

    try:
        package_modules.append(__import__(name))
    except ModuleNotFoundError:
        return package_objects

    for package_module in package_modules:
        for package_object_tuple in inspect.getmembers(package_module):
            object_name = package_object_tuple[0]
            package_object = package_object_tuple[1]
            # If the object is a function or a class
            if inspect.isfunction(package_object) or inspect.isclass(package_object):
                if (
                    object_name not in package_objects.keys()
                    and name in package_object.__module__
                ):
                    # Try to load the object from the module instead of the
                    # submodules.
                    if (
                        hasattr(package_module, "__all__")
                        and object_name in package_module.__all__
                    ):
                        package_objects[
                            object_name
                        ] = f"from {package_module.__name__} import {object_name}"
                    else:
                        package_objects[
                            object_name
                        ] = f"from {package_object.__module__} import {object_name}"

            elif not re.match(r"^_.*", object_name):
                # The rest of objects
                package_objects[
                    object_name
                ] = f"from {package_module.__name__} import {object_name}"

        for module in inspect.getmembers(package_module, inspect.ismodule):
            if module[1].__package__ == name:
                package_modules.append(module[1])
    return package_objects
