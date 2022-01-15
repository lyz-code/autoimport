"""Command line interface definition."""

import logging
from io import TextIOWrapper
from pathlib import Path
from typing import Any, Optional, Sequence, Tuple, Union

import click
from maison.config import ProjectConfig

from autoimport import services, version

log = logging.getLogger(__name__)

FileStreams = Union[TextIOWrapper, Sequence[TextIOWrapper]]
NestedSequence = Sequence[FileStreams]


def get_files(source_path: str) -> Sequence[TextIOWrapper]:
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
        self, value: Any, param: Optional[click.Parameter], ctx: Optional[click.Context]
    ) -> FileStreams:
        """Convert the value to the correct type."""
        try:
            return click.File("r+").convert(value, param, ctx)
        except click.BadParameter:
            path = click.Path(exists=True).convert(value, param, ctx)
            return get_files(path)


@click.command()
@click.version_option(version="", message=version.version_info())
@click.option("--config-file", default=None)
@click.argument("files", type=FileOrDir(), nargs=-1)
def cli(files: NestedSequence, config_file: Optional[str] = None) -> None:
    """Corrects the source code of the specified files."""
    flattened_files = flatten(files)
    config = ProjectConfig(
        project_name="autoimport",
        source_files=[config_file] if config_file else None,
    ).to_dict()
    try:
        fixed_code = services.fix_files(flattened_files, config)
    except FileNotFoundError as error:
        log.error(error)

    if fixed_code is not None:
        print(fixed_code, end="")


if __name__ == "__main__":  # pragma: no cover
    cli()  # pylint: disable=E1120
