"""Command line interface definition."""

import logging
from pathlib import Path
from typing import IO, Any, Dict, List, Optional, Sequence, Tuple, Union

import click

# Migrate away from xdg to xdg-base-dirs once only Python >= 3.10 is supported
# https://github.com/lyz-code/autoimport/issues/239
import xdg

from autoimport import services, version

log = logging.getLogger(__name__)


def get_files(source_path: str) -> List[IO[Any]]:
    """Get all files recursively from the given source path."""
    files = []
    for py_file in Path(source_path).glob("**/*.py"):
        if py_file.is_file():
            files.append(click.File("r+").convert(py_file, None, None))
    return files


def flatten(seq: Sequence[Any]) -> Tuple[Any, ...]:
    """Flatten nested sequences."""
    flattened = []
    for items in seq:
        if isinstance(items, (tuple, list)):
            for item in items:
                flattened.append(item)
        else:
            item = items
            flattened.append(item)
    return tuple(flattened)


class FileOrDir(click.ParamType):
    """Custom parameter type that accepts either a directory or file."""

    def convert(
        self,
        value: Union[str, Path],
        param: Optional[click.Parameter],
        ctx: Optional[click.Context],
    ) -> List[IO[Any]]:
        """Convert the value to the correct type."""
        try:
            return [click.File("r+").convert(value, param, ctx)]
        except click.BadParameter:
            path = click.Path(exists=True).convert(value, param, ctx)
            return get_files(str(path))


def get_config(
    package_name: str, source_files: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Get the configuration for a package."""
    # pylint: disable=import-outside-toplevel
    try:
        from maison.config import UserConfig  # type: ignore[attr-defined,unused-ignore]

        return UserConfig(
            package_name=package_name, source_files=source_files, merge_configs=True
        ).values
    except ImportError:
        from maison.config import (  # type: ignore[attr-defined,unused-ignore]
            ProjectConfig,
        )

        return ProjectConfig(
            project_name=package_name, source_files=source_files, merge_configs=True
        ).to_dict()


@click.command()
@click.version_option(version="", message=version.version_info())
@click.option("--config-file", default=None)
@click.option("--ignore-init-modules", is_flag=True, help="Ignore __init__.py files.")
@click.option(
    "--keep-unused-imports",
    is_flag=True,
    help="If True, retains unused imports.",
    default=False,
)
@click.argument("files", type=FileOrDir(), nargs=-1)
def cli(
    files: List[IO[Any]],
    config_file: Optional[str] = None,
    ignore_init_modules: bool = False,
    keep_unused_imports: bool = False,
) -> None:
    """Corrects the source code of the specified files."""
    # Compose configuration
    config_files: List[str] = []

    global_config_path = xdg.xdg_config_home() / "autoimport" / "config.toml"
    if global_config_path.is_file():
        config_files.append(str(global_config_path))

    config_files.append("pyproject.toml")

    if config_file is not None:
        config_files.append(config_file)

    config = get_config(package_name="autoimport", source_files=config_files)

    # Process inputs
    flattened_files = flatten(files)
    if ignore_init_modules:
        flattened_files = tuple(
            file for file in flattened_files if "__init__.py" not in file.name
        )

    try:
        fixed_code = services.fix_files(flattened_files, config, keep_unused_imports)
    except FileNotFoundError as error:
        log.error(error)

    if fixed_code is not None:
        print(fixed_code, end="")


if __name__ == "__main__":  # pragma: no cover
    cli()  # pylint: disable=E1120
