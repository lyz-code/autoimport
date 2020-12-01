"""Tests the service layer."""

from textwrap import dedent

from autoimport.services import fix_code


def test_fix_code_adds_missing_import() -> None:
    """Understands that os is a package and add it to the top of the file."""
    source = "os.getcwd()"
    fixed_source = dedent(
        """\
        import os

        os.getcwd()"""
    )

    result = fix_code(source)

    assert result == fixed_source


def test_fix_doesnt_change_source_if_package_doesnt_exist() -> None:
    """As foo is not found, nothing is changed."""
    source = "foo"

    result = fix_code(source)

    assert result == source


def test_fix_imports_packages_below_docstring() -> None:
    """Imports are located below the module docstrings."""
    source = dedent(
        '''\
        """Module docstring

        """
        import pytest
        os.getcwd()'''
    )
    fixed_source = dedent(
        '''\
        """Module docstring

        """

        import os

        os.getcwd()'''
    )

    result = fix_code(source)

    assert result == fixed_source


def test_fix_imports_packages_below_single_line_docstring() -> None:
    """Imports are located below the module docstrings when they only take one line."""
    source = dedent(
        '''\
        """Module docstring."""

        import pytest
        os.getcwd()'''
    )
    fixed_source = dedent(
        '''\
        """Module docstring."""

        import os

        os.getcwd()'''
    )

    result = fix_code(source)

    assert result == fixed_source


def test_fix_imports_type_hints() -> None:
    """Typing objects are initialized with their required header."""
    source = dedent(
        """\
        def function(dictionary: Dict) -> None:
            pass"""
    )
    fixed_source = dedent(
        """\
        from typing import Dict

        def function(dictionary: Dict) -> None:
            pass"""
    )

    result = fix_code(source)

    assert result == fixed_source


def test_fix_substitutes_aliases() -> None:
    """Missing import statements are loaded from the alias if there is a match."""
    source = """getcwd()"""
    aliases = {"getcwd": "from os import getcwd"}
    fixed_source = dedent(
        """\
        from os import getcwd

        getcwd()"""
    )

    result = fix_code(source, aliases)

    assert result == fixed_source


def test_fix_doesnt_fail_if_object_not_in_aliases() -> None:
    """If no aliases are found for the required object, do nothing."""
    source = """getcwd()"""
    aliases = {"Dict": "from Typing import Dict"}

    result = fix_code(source, aliases)

    assert result == source


def test_fix_removes_unneeded_imports() -> None:
    """If there is an import statement of an unused package it should be removed."""
    source = dedent(
        """\
        import requests
        foo = 1"""
    )
    fixed_source = "foo = 1"

    result = fix_code(source)

    assert result == fixed_source


def test_fix_removes_unneeded_imports_in_from_statements() -> None:
    """Remove `from package import` statement of an unused packages."""
    source = dedent(
        """\
        from os import path
        foo = 1"""
    )
    fixed_source = "foo = 1"

    result = fix_code(source)

    assert result == fixed_source


def test_fix_removes_unneeded_imports_in_beginning_of_from_statements() -> None:
    """Remove unused `object_name` in `from package import object_name, other_object`
    statements.
    """
    source = dedent(
        """\
        from os import path, getcwd

        getcwd()"""
    )
    fixed_source = dedent(
        """\
        from os import getcwd

        getcwd()"""
    )

    result = fix_code(source)

    assert result == fixed_source


def test_fix_removes_unneeded_imports_in_middle_of_from_statements() -> None:
    """Remove unused `object_name` in
    `from package import other_object, object_name, other_used_object` statements.
    """
    source = dedent(
        """\
        from os import getcwd, path, mkdir

        getcwd()
        mkdir()"""
    )
    fixed_source = dedent(
        """\
        from os import getcwd, mkdir

        getcwd()
        mkdir()"""
    )

    result = fix_code(source)

    assert result == fixed_source


def test_fix_removes_unneeded_imports_in_end_of_from_statements() -> None:
    """Remove unused `object_name` in `from package import other_object, object_name`
    statements.
    """
    source = dedent(
        """\
        from os import getcwd, path

        getcwd()"""
    )
    fixed_source = dedent(
        """\
        from os import getcwd

        getcwd()"""
    )

    result = fix_code(source)

    assert result == fixed_source


def test_fix_respects_multiple_from_import_lines() -> None:
    """
    Given: Multiple from X import Y lines.
    When: Fix code is run
    Then: The import statements aren't broken
    """
    source = dedent(
        """\
        from os import getcwd

        from re import match

        getcwd()
        match(r'a', 'a')"""
    )

    result = fix_code(source)

    assert result == source


def test_fix_respects_multiple_from_import_lines_in_multiple_lines() -> None:
    """
    Given: Multiple from X import Y lines, some with multiline format.
    When: Fix code is run
    Then: The import statements aren't broken
    """
    source = dedent(
        """\
        from os import (
            getcwd,
        )

        from re import match

        getcwd()
        match(r'a', 'a')"""
    )

    result = fix_code(source)

    assert result == source


def test_fix_respects_import_lines_in_multiple_line_strings() -> None:
    """
    Given: Import lines in several multiline strings.
    When: Fix code is run.
    Then: The import statements inside the string are not moved to the top.
    """
    source = dedent(
        """\
        from textwrap import dedent

        source = dedent(
            \"\"\"\\
            from re import match

            match(r'a', 'a')\"\"\"
        )

        source = dedent(
            \"\"\"\\
            from os import (
                getcwd,
            )

            getcwd()\"\"\"
        )"""
    )
    fixed_source = dedent(
        """\
        from textwrap import dedent

        source = dedent(
            \"\"\"\\
            from re import match

            match(r'a', 'a')\"\"\"
        )

        source = dedent(
            \"\"\"\\
            from os import (
                getcwd,
            )

            getcwd()\"\"\"
        )"""
    )

    result = fix_code(source)

    assert result == fixed_source


def test_fix_moves_import_statements_to_the_top() -> None:
    """Move import statements present in the source code to the top of the file"""
    source = dedent(
        """\
        a = 3

        import os
        os.getcwd()"""
    )
    fixed_source = dedent(
        """\
        import os

        a = 3

        os.getcwd()"""
    )

    result = fix_code(source)

    assert result == fixed_source


def test_fix_moves_import_statements_in_indented_code_to_the_top() -> None:
    """Move import statements present indented in the source code
    to the top of the file
    """
    source = dedent(
        """\
        a = 3


        def test():
            import os
            os.getcwd()"""
    )
    fixed_source = dedent(
        """\
        import os

        a = 3


        def test():
            os.getcwd()"""
    )

    result = fix_code(source)

    assert result == fixed_source


def test_fix_moves_from_import_statements_to_the_top() -> None:
    """Move from import statements present in the source code to the top of the file"""
    source = dedent(
        """\
        a = 3

        from os import getcwd
        getcwd()"""
    )
    fixed_source = dedent(
        """\
        from os import getcwd

        a = 3

        getcwd()"""
    )

    result = fix_code(source)

    assert result == fixed_source


def test_fix_doesnt_break_objects_with_import_in_their_names() -> None:
    """Objects that have the import name in their name should not be changed."""
    source = dedent(
        """\
        def import_code():
            pass

        def code_import():
            pass

        def import():
            pass

        import_string = 'a'"""
    )

    result = fix_code(source)

    assert result == source


def test_fix_doesnt_move_import_statements_with_noqa_to_the_top() -> None:
    """Ignore lines that have # noqa: autoimport."""
    source = dedent(
        """\
        a = 3

        from os import getcwd # noqa: autoimport
        getcwd()"""
    )

    result = fix_code(source)

    assert result == source


def test_fix_respects_noqa_in_from_import_lines_in_multiple_lines() -> None:
    """
    Given: Multiple from X import Y lines, some with multiline format with noqa
        statement.
    When: Fix code is run.
    Then: The import statements aren't broken.
    """
    source = dedent(
        """\
        from os import getcwd

        getcwd()

        from re import ( # noqa: autoimport
            match,
        )

        match(r'a', 'a')"""
    )

    result = fix_code(source)

    assert result == source


def test_fix_respects_strings_with_import_statements() -> None:
    """
    Given: Code with a string that has import statements structure.
    When: Fix code is run.
    Then: The string is respected
    """
    source = dedent(
        """\
        import_string = 'import requests'
        from_import_string = "from re import match"
        multiline string = dedent(
            \"\"\"\\
            import requests
            from re import match
            \"\"\"
        )
        multiline single_quote_string = dedent(
            \'\'\'\\
            import requests
            from re import match
            \'\'\'
        )
        import os"""
    )
    fixed_source = dedent(
        """\
        import os

        import_string = 'import requests'
        from_import_string = "from re import match"
        multiline string = dedent(
            \"\"\"\\
            import requests
            from re import match
            \"\"\"
        )
        multiline single_quote_string = dedent(
            \'\'\'\\
            import requests
            from re import match
            \'\'\'
        )"""
    )

    result = fix_code(source)

    assert result == fixed_source


def test_fix_doesnt_mistake_docstrings_with_multiline_string() -> None:
    """
    Given: A function with a docstring.
    When: Fix code is run.
    Then: The rest of the file is not mistaken for a long multiline string
    """
    source = dedent(
        """\
        def function_1():
            \"\"\"Function docstring\"\"\"
            import os
            os.getcwd()"""
    )
    fixed_source = dedent(
        """\
        import os

        def function_1():
            \"\"\"Function docstring\"\"\"
            os.getcwd()"""
    )

    result = fix_code(source)

    assert result == fixed_source
