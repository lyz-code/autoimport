"""Command line interface definition."""

import logging
from typing import Optional, Tuple

import click
from maison.config import ProjectConfig

from autoimport import services, version

log = logging.getLogger(__name__)


@click.command()
@click.version_option(version="", message=version.version_info())
@click.option("--config-file", default=None)
@click.argument("files", type=click.File("r+"), nargs=-1)
def cli(files: Tuple[str], config_file: Optional[str] = None) -> None:
    """Corrects the source code of the specified files."""
    config = ProjectConfig(
        project_name="autoimport",
        source_files=[config_file] if config_file else None,
    ).to_dict()
    try:
        fixed_code = services.fix_files(files, config)
    except FileNotFoundError as error:
        log.error(error)

    if fixed_code is not None:
        print(fixed_code, end="")


if __name__ == "__main__":  # pragma: no cover
    cli()  # pylint: disable=E1120
