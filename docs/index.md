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

# A Simple Example

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
    using [isort](https://pycqa.github.io/isort) afterwards to clean the file.

# References

As most open sourced programs, `autoimport` is standing on the shoulders of
giants, namely:

[autoflake](https://pypi.org/project/autoflake/)
: Inspiration of `autoimport`. Also used their code to interact with
[pyflakes](https://pypi.org/project/pyflakes/).

[Click](https://click.palletsprojects.com/)
: Used to create the command line interface.

# Contributing

For guidance on setting up a development environment and how to make
a contribution to *autoimport*, see [Contributing to
autoimport](https://lyz-code.github.io/autoimport/contributing/).
