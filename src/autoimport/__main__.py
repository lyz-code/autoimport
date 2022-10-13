"""Entrypoint to allow running as `python3 -m autoimport`."""

from autoimport.entrypoints.cli import cli

if __name__ == "__main__":
    # this needs no-value-for-parameter exclusion because pylint
    # isn't smart enough to realize that click decorator handles it (but mypy is)
    cli()  # pylint: disable=no-value-for-parameter
