"""Store the classes and fixtures used throughout the tests."""

from pathlib import Path
from typing import Callable, Optional

import pytest


@pytest.fixture()
def create_tmp_file(tmp_path: Path) -> Callable:
    """Fixture for creating a temporary file."""

    def _create_tmp_file(
        content: Optional[str] = "", filename: Optional[str] = "file.txt"
    ) -> Path:
        tmp_file = tmp_path / filename
        tmp_file.write_text(content)
        return tmp_file

    return _create_tmp_file
