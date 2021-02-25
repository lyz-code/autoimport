[![Actions Status](https://github.com/lyz-code/autoimport/workflows/Tests/badge.svg)](https://github.com/lyz-code/autoimport/actions)
[![Actions Status](https://github.com/lyz-code/autoimport/workflows/Build/badge.svg)](https://github.com/lyz-code/autoimport/actions)
[![Coverage Status](https://coveralls.io/repos/github/lyz-code/autoimport/badge.svg?branch=master)](https://coveralls.io/github/lyz-code/autoimport?branch=master)

Autoimport missing python libraries.

Throughout the development of a python program you continuously need to manage
the python import statements either because you need one new object or because
you no longer need it. This means that you need to stop writing whatever you
were writing, go to the top of the file, create or remove the import statement
and then resume coding.

This workflow break is annoying and almost always unnecessary. `autoimport`
solves this problem if you execute it whenever you have an import error, for
example by configuring your editor to run it when saving the file.

# Installing

```bash
pip install autoimport
```

# Usage

Imagine we've got the following source code:

```python
import requests


def hello(names: Tuple[str]) -> None:
    for name in names:
        print(f"Hi {name}!")

os.getcwd()
```

It has the following import errors:

* `requests` is imported but unused.
* `os` and `Tuple` are needed but not imported.

After running `autoimport` the resulting source code will be:

```python
import os
from typing import Tuple


def hello(names: Tuple[str]) -> None:
    for name in names:
        print(f"Hi {name}!")

os.getcwd()
```

`autoimport` can be used both as command line tool and as a library.

* As a command line tool:

    ```bash
    $: autoimport file.py
    ```

* As a library:

    ```python
    from autoimport import fix_files

    fix_files(['file.py'])
    ```

!!! warning ""
    `autoimport` will add all dependencies at the top of the file, we suggest
    using [isort](https://pycqa.github.io/isort) and
    [black](https://black.readthedocs.io/en/stable/) afterwards to clean the
    file.

# Features

## Add missing imports

`autoimport` matches each of the missing import statements against the following
objects:

* The modules referenced in `PYTHONPATH`.
* The `typing` library objects.
* The common statements.

    Where some of the common statements are:

        * `BeautifulSoup` -> `from bs4 import BeautifulSoup`
        * `call` -> `from unittest.mock import call`
        * `CaptureFixture` -> `from _pytest.capture import CaptureFixture`
        * `CliRunner` -> `from click.testing import CliRunner`
        * `copyfile` -> `from shutil import copyfile`
        * `dedent` -> `from textwrap import dedent`
        * `LocalPath` -> `from py._path.local import LocalPath`
        * `LogCaptureFixture` -> `from _pytest.logging import LogCaptureFixture`
        * `Mock` -> `from unittest.mock import Mock`
        * `patch` -> `from unittest.mock import patch`
        * `StringIO` -> `from io import StringIO`
        * `TempdirFactory` -> `from _pytest.tmpdir import TempdirFactory`
        * `YAMLError` -> `from yaml import YAMLError`

* The objects of the Python project you are developing, assuming you are
    executing the program in a directory of the project and you can import it.

!!! warning "It may not work if you use pip install -e ."

    Given that you execute `autoimport` inside a virtualenv where the package is
    installed with `pip install -e .`, when there is an import error in a file
    that is indexed in the package, `autoimport` won't be able to read the
    package contents as the `import` statement will fail. So it's a good idea to
    run autoimport from a virtualenv that has a stable version of the package we
    are developing.

## Remove unused import statements

If an object is imported but unused, `autoimport` will remove the import
statement.

## Moving the imports to the top

There are going to be import cases that may not work, if you find one, please
[open an
issue](https://github.com/lyz-code/autoimport/issues/new?labels=bug&template=bug.md).

While we fix it you can write the import statement wherever you are in the file
and the next time you run `autoimport` it will get moved to the top.

If you don't want a specific line to go to the top, add the `# noqa: autoimport`
at the end. For example:

```python
a = 1

from os import getcwd # noqa: autoimport

getcwd()
```

# References

As most open sourced programs, `autoimport` is standing on the shoulders of
giants, namely:

[autoflake](https://pypi.org/project/autoflake/)
: Inspiration of `autoimport`. Also used their code to interact with
[pyflakes](https://pypi.org/project/pyflakes/).

[Click](https://click.palletsprojects.com/)
: Used to create the command line interface.

[Pytest](https://docs.pytest.org/en/latest)
: Testing framework, enhanced by the awesome
    [pytest-cases](https://smarie.github.io/python-pytest-cases/) library that made
    the parametrization of the tests a lovely experience.

[Mypy](https://mypy.readthedocs.io/en/stable/)
: Python static type checker.

[Flakehell](https://github.com/life4/flakehell)
: Python linter with [lots of
    checks](https://lyz-code.github.io/blue-book/devops/flakehell/#plugins).

[Black](https://black.readthedocs.io/en/stable/)
: Python formatter to keep a nice style without effort.

[Autoimport](https://github.com/lyz-code/autoimport)
: Python formatter to automatically fix wrong import statements.

[isort](https://github.com/timothycrosley/isort)
: Python formatter to order the import statements.

[Pip-tools](https://github.com/jazzband/pip-tools)
: Command line tool to manage the dependencies.

[Mkdocs](https://www.mkdocs.org/)
: To build this documentation site, with the
[Material theme](https://squidfunk.github.io/mkdocs-material).

[Safety](https://github.com/pyupio/safety)
: To check the installed dependencies for known security vulnerabilities.

[Bandit](https://bandit.readthedocs.io/en/latest/)
: To finds common security issues in Python code.

[Yamlfix](https://github.com/lyz-code/yamlfix)
: YAML fixer.

# Alternatives

If you like the idea but not how we solved the problem, take a look at this
other solutions:

* [smart-imports](https://github.com/Tiendil/smart-imports)

# Contributing

For guidance on setting up a development environment, and how to make
a contribution to *autoimport*, see [Contributing to
autoimport](https://lyz-code.github.io/autoimport/contributing).
