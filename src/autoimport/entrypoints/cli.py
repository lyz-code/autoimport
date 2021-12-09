"""Command line interface definition."""

import logging
from typing import Optional, Tuple

import click

from autoimport import services, version

log = logging.getLogger(__name__)


@click.command()
@click.version_option(version="", message=version.version_info())
@click.option(
    "--config-file",
    default=None,
    help="File to read config from, instead of `./pyproject.toml`",
)
@click.option(
    "--no-global-config",
    is_flag=True,
    default=False,
    help=f"Disable reading `{services.GLOBAL_CONFIG_PATH}`",
)
@click.argument("files", type=click.File("r+"), nargs=-1)
def cli(
    files: Tuple[str],
    config_file: Optional[str] = None,
    no_global_config: bool = False,
) -> None:
    """Corrects the source code of the specified files."""
    config = services.read_configs(
        config_file=config_file,
        no_global_config=no_global_config,
    )
    try:
        fixed_code = services.fix_files(files, config)
    except FileNotFoundError as error:
        log.error(error)

    if fixed_code is not None:
        print(fixed_code, end="")


if __name__ == "__main__":  # pragma: no cover
    cli()  # pylint: disable=E1120
