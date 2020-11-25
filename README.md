# Autoimport

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

## Help

See [documentation](https://lyz-code.github.io/autoimport) for more details.

## Installing

```bash
pip install autoimport
```

## Contributing

For guidance on setting up a development environment, and how to make
a contribution to *autoimport*, see [Contributing to
autoimport](https://lyz-code.github.io/autoimport/contributing).

## License

GPLv3
