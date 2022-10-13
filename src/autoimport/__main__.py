"""Entrypoint to allow running as `python3 -m autoimport`."""

from autoimport.entrypoints.cli import cli

if __name__ == "__main__":
    cli()
