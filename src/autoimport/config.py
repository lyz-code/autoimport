"""Module to hold the `AutoImportConfig` class definition."""

from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import toml

from autoimport.utils import get_pyproject_path


class Config:
    """Defines the base `Config` and provides accessors to get config values."""

    def __init__(
        self,
        config_dict: Optional[Dict[str, Any]] = None,
        config_path: Optional[Path] = None,
    ) -> None:
        """Initialize the config."""
        self._config_dict: Dict[str, Any] = config_dict or {}
        self.config_path: Optional[Path] = config_path

    def get_option(self, option: str) -> Optional[str]:
        """Return the value of a config option.

        Args:
            option (str): the config option for which to return the value

        Returns:
            The value of the given config option or `None` if it doesn't exist
        """
        return self._config_dict.get(option)


class AutoImportConfig(Config):
    """Defines the autoimport `Config`."""

    def __init__(self, starting_path: Optional[Path] = None) -> None:
        """Initialize the config."""
        config_path, config_dict = _find_config(starting_path)
        super().__init__(config_dict=config_dict, config_path=config_path)


def _find_config(
    starting_path: Optional[Path] = None,
) -> Tuple[Optional[Path], Dict[str, Any]]:
    pyproject_path: Optional[Path] = get_pyproject_path(starting_path)
    if pyproject_path:
        return pyproject_path, toml.load(pyproject_path).get("tool", {}).get(
            "autoimport", {}
        )

    return None, {}


autoimport_config: AutoImportConfig = AutoImportConfig()
