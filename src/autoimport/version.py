__version__ = "0.1.0"


def version_info() -> str:
    import platform
    import sys

    info = {
        "repository-pattern version": __version__,
        "python version": sys.version,
        "platform": platform.platform(),
    }
    return "\n".join(
        "{:>30} {}".format(k + ":", str(v).replace("\n", " ")) for k, v in info.items()
    )
