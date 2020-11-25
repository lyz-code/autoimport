"""
Module to store the functions shared by the different entrypoints.
"""

import logging
import sys

log = logging.getLogger(__name__)


def load_logger(verbose: bool = False) -> None:
    """
    Function to configure the Logging logger.
    """

    logging.addLevelName(logging.INFO, "[\033[36m+\033[0m]")
    logging.addLevelName(logging.ERROR, "[\033[31m+\033[0m]")
    logging.addLevelName(logging.DEBUG, "[\033[32m+\033[0m]")
    logging.addLevelName(logging.WARNING, "[\033[33m+\033[0m]")
    if verbose:
        logging.basicConfig(
            stream=sys.stderr, level=logging.DEBUG, format="  %(levelname)s %(message)s"
        )
        logging.getLogger("alembic").setLevel(logging.INFO)
    else:
        logging.basicConfig(
            stream=sys.stderr, level=logging.INFO, format="  %(levelname)s %(message)s"
        )
        logging.getLogger("alembic").setLevel(logging.WARNING)
