"""Command line interface definition."""

import logging
from typing import Tuple

import click
from maison.config import ProjectConfig

from autoimport import services, version

log = logging.getLogger(__name__)


@click.command()
@click.version_option(version="", message=version.version_info())
@click.argument("files", type=click.File("r+"), nargs=-1)
def cli(files: Tuple[str]) -> None:
    """Corrects the source code of the specified files."""
    config = ProjectConfig(project_name="autoimport").to_dict()
    try:
        fixed_code = services.fix_files(files, config)
    except FileNotFoundError as error:
        log.error(error)

    if fixed_code is not None:
        print(fixed_code, end="")


if __name__ == "__main__":  # pragma: no cover
    cli()  # pylint: disable=E1120
