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
