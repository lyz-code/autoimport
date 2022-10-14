"""Tests the service layer."""

from textwrap import dedent

import pytest

from autoimport.model import common_statements
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
        """Module docstring.

        """
        import pytest
        os.getcwd()'''
    )
    fixed_source = dedent(
        '''\
        """Module docstring.

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


def test_fix_removes_multiple_unneeded_imports() -> None:
    """
    Given: A source code with multiple unused import statements.
    When: fix_code is run.
    Then: The unused import statements are deleted.
    """
    source = dedent(
        """\
        import requests
        from textwrap import dedent

        from yaml import YAMLError
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


def test_fix_removes_unused_imports_in_multiline_from_statements() -> None:
    """
    Given: A source code with multiline import from statements.
    When: fix_code is run
    Then: Unused import statements are deleted
    """
    source = dedent(
        """\
        from os import (
            getcwd,
            path,
        )

        getcwd()"""
    )
    fixed_source = dedent(
        """\
        from os import (
            getcwd,
        )


        getcwd()"""
    )

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
        import requests

        requests.get('hi')

        def test():
            import os
            os.getcwd()"""
    )
    fixed_source = dedent(
        """\
        import requests

        import os


        requests.get('hi')

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


def test_fix_moves_multiline_import_statements_to_the_top() -> None:
    """
    Given: Multiple from X import Y lines.
    When: Fix code is run.
    Then: The import statements are moved to the top.
    """
    source = dedent(
        """\
        from os import getcwd

        getcwd()

        from re import (
            match,
        )
        match(r'a', 'a')"""
    )
    fixed_source = dedent(
        """\
        from os import getcwd

        from re import (
            match,
        )


        getcwd()

        match(r'a', 'a')"""
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


def test_fix_doesnt_fail_on_noqa_lines_on_unused_import() -> None:
    """Ignore lines that have # noqa: autoimport."""
    source = dedent(
        """\
        from os import getcwd # noqa: autoimport"""
    )

    result = fix_code(source)

    assert result == source


def test_fix_respects_fmt_skip_lines() -> None:
    """Ignore lines that have # fmt: skip."""
    source = dedent(
        """
        def why():
            import pdb;pdb.set_trace()  # fmt: skip
            return 'dunno'
        """
    ).replace("\n", "", 1)

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


@pytest.mark.parametrize(
    ("import_key", "import_statement"),
    ((key, value) for key, value in common_statements.items()),
    ids=list(common_statements.keys()),
)
def test_fix_autoimports_common_imports(import_key: str, import_statement: str) -> None:
    """
    Given: Code with missing import statements that match the common list.
    When: Fix code is run.
    Then: The imports are done
    """
    source = dedent(
        f"""\
        import os

        os.getcwd

        variable = {import_key}"""
    )
    fixed_source = dedent(
        f"""\
        import os

        {import_statement}


        os.getcwd

        variable = {import_key}"""
    )

    result = fix_code(source)

    assert result == fixed_source


def test_fix_autoimports_objects_defined_in_the_root_of_the_package() -> None:
    """
    Given:
        The fix code is run from a directory that belongs to a python project package.
        And a source code with an object that needs an import statement.
        And that object belongs to the root of the python package.
    When: Fix code is run.
    Then: The import is done
    """
    source = dedent(
        """\
        fix_code()"""
    )
    fixed_source = dedent(
        """\
        from autoimport import fix_code


        fix_code()"""
    )

    result = fix_code(source)

    assert result == fixed_source


def test_fix_autoimports_objects_defined_in___all__special_variable() -> None:
    """
    Given: Some missing packages in the __all__ variable
    When: Fix code is run.
    Then: The import is done
    """
    source = dedent(
        """\
        __all__ = ['fix_code']"""
    )
    fixed_source = dedent(
        """\
        from autoimport import fix_code


        __all__ = ['fix_code']"""
    )

    result = fix_code(source)

    assert result == fixed_source


def test_fix_respects_type_checking_import_statements() -> None:
    """
    Given: Code with if TYPE_CHECKING imports
    When: Fix code is run.
    Then: The imports are not moved above the if statement.
    """
    source = dedent(
        """\
        import os
        from typing import TYPE_CHECKING

        if TYPE_CHECKING:
            from .model import Book


        os.getcwd()


        def read_book(book: Book):
            pass"""
    )

    result = fix_code(source)

    assert result == source


def test_fix_respects_multiparagraph_type_checking_import_statements() -> None:
    """
    Given: Code with two paragraphs of imports inside an if TYPE_CHECKING block
    When: Fix code is run.
    Then: The imports are not moved above the if statement.
    """
    source = dedent(
        """\
        import os
        from typing import TYPE_CHECKING

        if TYPE_CHECKING:
            from .model import Book

            from other import Other


        os.getcwd()


        def read_book(book: Book, other: Other):
            pass"""
    )

    result = fix_code(source)

    assert result == source


def test_fix_respects_try_except_in_import_statements() -> None:
    """
    Given: Code with try except statements in the imports.
    When: Fix code is run
    Then: The try except statements are respected
    """
    source = dedent(
        """\
        import os

        try:
            from typing import TypedDict  # noqa
        except ImportError:
            from mypy_extensions import TypedDict  # <=3.7


        os.getcwd()
        Movie = TypedDict('Movie', {'name': str, 'year': int})"""
    )

    result = fix_code(source)

    assert result == source


def test_fix_respects_leading_comments() -> None:
    """
    Given: Code with initial comments like shebang and editor configuration.
    When: Fix code is run
    Then: The comment statements are respected
    """
    source = dedent(
        '''\
        #!/usr/bin/env python3
        # -*- coding: latin-1 -*-
        """docstring"""
        print(os.path.exists("."))'''
    )
    desired_source = dedent(
        '''\
        #!/usr/bin/env python3
        # -*- coding: latin-1 -*-
        """docstring"""

        import os


        print(os.path.exists("."))'''
    )

    result = fix_code(source)

    assert result == desired_source


def test_fix_respects_leading_comments_with_new_lines() -> None:
    """
    Given: Code with initial comments with new lines and a trailing newline.
    When: Fix code is run.
    Then: The comment statements and trailing newline are respected.
    """
    source = dedent(
        '''\
        #!/usr/bin/env python3
        # -*- coding: latin-1 -*-

        # pylint: disable=foobar

        """

        This is the docstring.

        """

        import sys

        print(os.path.exists(sys.argv[1]))
        '''
    )
    desired_source = dedent(
        '''\
        #!/usr/bin/env python3
        # -*- coding: latin-1 -*-

        # pylint: disable=foobar

        """

        This is the docstring.

        """

        import sys

        import os


        print(os.path.exists(sys.argv[1]))
        '''
    )

    result = fix_code(source)

    assert result == desired_source


def test_fix_imports_dependency_only_once() -> None:
    """
    Given: Code with a line that uses a package three times.
    When: Fix code is run.
    Then: The dependency is imported only once
    """
    source = dedent(
        """\
        def f(x):
            return os.getcwd() + os.getcwd() + os.getcwd()
        """
    )
    desired_source = dedent(
        """\
        import os


        def f(x):
            return os.getcwd() + os.getcwd() + os.getcwd()
        """
    )

    result = fix_code(source)

    assert result == desired_source


def test_fix_doesnt_fail_on_empty_file() -> None:
    """
    Given: An empty file
    When: Fix code is run.
    Then: The output doesn't change
    """
    source = ""

    result = fix_code(source)

    assert result == source


def test_file_that_only_has_unused_imports() -> None:
    """
    Given: A file that only has unused imports.
    When: Fix code is run.
    Then: The output should be a single empty line.
    """
    source = dedent(
        """\
        import os
        import sys
        """
    )

    result = fix_code(source)

    assert result == "\n"


def test_file_with_common_statement() -> None:
    """
    Given: Code with a commonly-used object.
    When: Fix code is run.
    Then: The appropriate import statement from the common_statements dict is added.
    """
    source = dedent(
        """\
        BeautifulSoup
        """
    )
    desired_source = dedent(
        """\
        from bs4 import BeautifulSoup


        BeautifulSoup
        """
    )

    result = fix_code(source)

    assert result == desired_source


def test_file_with_custom_common_statement() -> None:
    """
    Given: Code that uses an undefined object called `FooBar`.
    When:
        Fix code is run and a `config` dict is passed specifying `FooBar` as a common
        statement.
    Then:
        The appropriate import statement from the common_statements dict is added.
    """
    source = dedent(
        """\
        FooBar
        """
    )
    custom_config = {"common_statements": {"FooBar": "from baz_qux import FooBar"}}
    desired_source = dedent(
        """\
        from baz_qux import FooBar


        FooBar
        """
    )

    result = fix_code(source, config=custom_config)

    assert result == desired_source


def test_file_with_comment_in_import() -> None:
    """
    Given: Code with a comment on two import statements
    When: Fix code is run.
    Then: The unused import line is removed with it's comment
    """
    source = dedent(
        """\
        import os  # comment 1
        import sys  # comment 2

        os.getcwd()
        """
    )
    desired_source = dedent(
        """\
        import os  # comment 1


        os.getcwd()
        """
    )

    result = fix_code(source)

    assert result == desired_source


def test_file_with_comment_in_from_import() -> None:
    """
    Given: Code with a comment on two import statements
    When: Fix code is run.
    Then: The unused import line is removed with it's comment
    """
    source = dedent(
        """\
        import os  # comment 1
        from textwrap import dedent # comment 2

        os.getcwd()
        """
    )
    desired_source = dedent(
        """\
        import os  # comment 1


        os.getcwd()
        """
    )

    result = fix_code(source)

    assert result == desired_source


def test_file_with_import_as() -> None:
    """
    Given: Code with an from x import y as z import statement
    When: Fix code is run.
    Then: The unused import line is removed
    """
    source = dedent(
        """\
        from subprocess import run as run
        """
    )

    result = fix_code(source)

    assert result == "\n"


def test_file_with_non_used_multiline_import() -> None:
    """
    Given: Code with a multiline from import where no one is used.
    When: Fix code is run.
    Then: The unused import line is removed
    """
    source = dedent(
        """\
        from foo import (
            bar,
            baz,
        )
        """
    )

    result = fix_code(source)

    assert result == "\n"


def test_file_with_import_and_seperator() -> None:
    """Ensure import lines with seperators are fixed correctly."""
    source = dedent(
        """
        a = 1
        import pdb;pdb.set_trace()
        b = 2
        """
    )
    expected = dedent(
        """
        import pdb


        a = 1
        pdb.set_trace()
        b = 2
        """
    ).replace("\n", "", 1)

    result = fix_code(source)

    assert result == expected


def test_file_with_import_and_seperator_indentation() -> None:
    """Ensure import lines with seperators are fixed correctly when indented."""
    source = dedent(
        """
        Class Person:
            import pdb; pdb.set_trace()
            def say_hi(self):
                print('hi')
        """
    )
    expected = dedent(
        """
        import pdb


        Class Person:
            pdb.set_trace()
            def say_hi(self):
                print('hi')
        """
    ).replace("\n", "", 1)

    result = fix_code(source)

    assert result == expected


def test_import_module_with_dot() -> None:
    """
    Given: An import file with an import with a dot
    When: running autoimport on the file
    Then: ValueError exception is not raised

    Tests https://github.com/lyz-code/autoimport/issues/225
    """
    source = dedent(
        """
        import my_module.m
        """
    )

    result = fix_code(source)

    assert result == "\n"


def test_respect_new_lines_between_imports_and_code() -> None:
    r"""
    Given: A file with two \n between imports and the code
    When: running autoimport on the file
    Then: the file is untouched

    For more info check https://github.com/lyz-code/autoimport/issues/219
    """
    source = dedent(
        """\
        import random


        def foo():
            print(random.random())
        """
    )

    result = fix_code(source)

    assert result == source
