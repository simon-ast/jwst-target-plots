import logging


def configure_logger(logfile_full: str) -> None:
    """Simple logger configuration."""
    logging.basicConfig(
        filename=logfile_full,
        filemode="w",
        format='%(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    return None
