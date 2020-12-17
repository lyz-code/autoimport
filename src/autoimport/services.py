"""Gather all the orchestration functionality required by the program to work.

Classes and functions that connect the different domain model objects with the adapters
and handlers to achieve the program's purpose.
"""

from typing import Optional, Tuple

from _io import TextIOWrapper

from autoimport.model import SourceCode


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


def fix_code(original_source_code: str) -> str:
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
    return SourceCode(original_source_code).fix()
