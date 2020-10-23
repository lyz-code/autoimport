"""Utilities to retrieve the information of the program version."""

import platform
import sys

__version__ = "0.1.0"


def version_info() -> str:
    """Display the version of the program, python and the platform."""
    info = {
        "repository-pattern version": __version__,
        "python version": sys.version.replace("\n", " "),
        "platform": platform.platform(),
    }
    return "\n".join(f"{k + ':' :>30} {v}" for k, v in info.items())
